from fabric.api import *
from fabric.tasks import execute
import os
import re

def get_platform():
    with hide('everything'):
        return run("uname -s")

def is_installed(cmd):
    with settings(warn_only=True):
        with hide('everything'):
            result = run('command -v ' + cmd)
            return result.return_code == 0
@task
@hosts('localhost')
def launch(cloud, num):
    if cloud == "azure":
        local('./azure-client.py launch -n ' + num)
    if cloud == "ec-2" or cloud == "ec2":
        local('./ec2-client.py launch -n ' + num)

@task 
@parallel
def install():
    ensure_hosts()
    platform = get_platform()
    put(local_path='installer/install-parser', remote_path='~/install-parser')
    r = run('cd ~; chmod +x ~/install-parser; ./install-parser')
    if not r.return_code == 0:
        print('ERROR. Aborting')
        sys.exit()    

@task
@parallel
def restage():
  ensure_hosts()
  with prefix('export PATH=~/jdk1.8.0_45/bin:$PATH'):
    r = run('cd ~/parser && sbt/sbt stage')
    if not r.return_code == 0:
      print('ERROR. Aborting')
      sys.exit()    
  
@task
@hosts('localhost')
def split(input='test/input.json',batch_size=1000):
    local('rm -rf segments')
    local('mkdir -p segments')
    local('cat ' + input + ' | shuf | split -a 5 -l ' + str(batch_size) + ' - segments/')

def get_remote_write_dir():
  if read_cloud() == 'ec-2':
    directory = '/mnt'
  else:
    directory = env.directories[env.host_string]
  return directory

@task
@parallel
def copy_to_servers():
    ensure_hosts()

    directory = get_remote_write_dir()
    user = run('whoami')
    run('sudo chown ' + user + ' ' + directory)
    run('rm -rf ' + directory + '/segments')
    run('mkdir -p ' + directory + '/segments')
    num_machines = len(env.all_hosts)
    machine = env.all_hosts.index(env.host_string)

    output = local('find segments -type f', capture=True)
    files = output.split('\n')
    for f in files:
        file_num = hash(f) 
        file_machine = file_num % num_machines
        if file_machine == machine:
            print "put %s on machine %d" % (f, file_machine)
            put(local_path=f, remote_path=directory + '/segments')

@task
@runs_once
def copy(input='test/input.json',batch_size=1000):
  execute(split, input=input, batch_size=batch_size)
  execute(copy_to_servers)

@task
@parallel
def echo():
    ensure_hosts()
    run('echo "$HOSTNAME"')

@task
@parallel
def parse(parallelism=2, key_id='item_id', content_id='content'):
    ensure_hosts()
    directory = get_remote_write_dir()
    with prefix('export PATH=~/jdk1.8.0_45/bin:$PATH'):
        run('find ' + directory + '/segments -name "*" -type f 2>/dev/null -print0 | ' +
          '(cd ~/parser && xargs -0 -P ' + str(parallelism) + ' -L1 bash -c \'./run.sh -i json -k ' +
          key_id + ' -v ' + content_id + ' -f \"$0\"\')')

@task
@parallel
def get_registers():
  directory = get_remote_write_dir()
  registers = run('find ' + directory + '/segments -name "*.reg" -type f 2>/dev/null -print0 | xargs -0 -L1 head', quiet=True)
  return [reg.strip() for reg in registers.split('\n')]

@task
@hosts('localhost')
def get_status():

  # Get total segments count
  total = len(filter(lambda f : re.search(r'\..*$', f) is None, os.listdir('segments')))

  # Get registers
  results = execute(get_registers)

  # Parse registers & save status report
  with open('parse_status.txt', 'wb') as f:
    completed = 0
    pending = 0
    for server_name, registers in results.iteritems():
      for reg in registers:
        if len(reg.strip()) == 0:
          continue
        seg, status_code = reg.split(':')
        status_code = int(status_code)
        completed += status_code
        pending += 1 - status_code
        status = "Completed" if status_code == 1 else "Pending"
        f.write("%s : %s [node=%s]\n" % (seg, status, server_name))
    percent_done = 100*(float(completed)/total) if total > 0 else 0.0
    print "\nStatus:"
    print "Completed segments: %s / %s (%d%%)" % (completed, total, percent_done)
    print "Currently processing: %s" % pending
    print "Detailed report written to parse_status.txt"

@task
@parallel
def clear_for_reparse():
  ensure_hosts()
  directory = get_remote_write_dir()
  run('rm -rf ' + directory + '/segments/*.parsed')
  run('rm -rf ' + directory + '/segments/*.failed')

@task
@parallel
def collect_from_nodes():
  ensure_hosts()
  directory = get_remote_write_dir()

  # collect all files ending in .parsed and .failed
  output = run('find ' + directory + '/segments/ -name "*.*" -type f')
  if output == '':
     print('Warning: No result segments on node') 
  else:
     files = output.rstrip().split('\r\n')
     for f in files:
         path = f 
         get(local_path='segments', remote_path=path)

@task
@hosts('localhost')
def cat_result():
  local('rm -f result')
  local('find ./segments -name "*.parsed" -type f -print0 | xargs -0 cat >>result')
  print('Done. You can now load the result into your database.')

@task
@runs_once
def collect():
  execute(collect_from_nodes)
  execute(cat_result)

def num_lines(filepath):
  with open(filepath, 'rb') as f:
    for i,l in enumerate(f):
      pass
  return i+1

# Large batch sizes seem to cause memory errors...
MAX_BATCH_SIZE=5000

@task
@hosts('localhost')
def copy_parse_collect(input=None, batch_size=None, parallelism=2, key_id='item_id', content_id='content'):
  """
  Wrapper function to split and copy file to servers, parse, and collect
  If batch_size is None, it will be automatically calculated based on number of machines
  and specified parallelism
  """
  if input is None:
    print('Please specify input file to parse.')
    exit(0)
  ensure_hosts()
  num_machines = num_lines('.state/HOSTS')
  print('Preparing to run on %s machines with PARALLELISM=%s' % (num_machines, parallelism))
  if batch_size is None:
    batch_size = min(num_lines(input) / (num_machines * int(parallelism)), MAX_BATCH_SIZE)

  # Copy the files to the remote machines
  execute(copy, input=input, batch_size=batch_size)
  
  # Sometimes coreNLP doesn't download- restage here to ensure compiled
  execute(restage)

  # Parse
  execute(parse, parallelism=parallelism, key_id=key_id, content_id=content_id)

  # Collect
  execute(collect)
  execute(get_status)

@task
@hosts('localhost')
def terminate():
    ensure_hosts()
    cloud = read_cloud()
    if cloud == 'azure':
        local('./azure-client.py terminate')
    elif cloud == 'ec-2':
        local('./ec2-client.py terminate')
    else:
        print('Unknown cloud: ' + cloud)
        exit(1)

def read_cloud():
    if not os.path.isfile('.state/CLOUD'): 
        print('Could not find .state/CLOUD. Did you launch your machines already?')
        exit(1)
    return open('.state/CLOUD', 'r').readlines()[0].rstrip()

def read_hosts():
    if os.path.isfile('.state/HOSTS'):
        env.hosts = open('.state/HOSTS', 'r').readlines()
        env.user = "ubuntu"
        env.key_filename = "./ssh/bazaar.key"
        dirs = open('.state/DIRS', 'r').readlines()
        env.directories = {}
        for i in range(0, len(dirs)):
            env.directories[env.hosts[i].rstrip()] = dirs[i].rstrip()
    else:
        env.hosts = []

def ensure_hosts():
    if not os.path.isfile('.state/HOSTS'): 
        print('Could not find .state/HOSTS. Did you launch your machines already?')
        exit(1)

read_hosts()
