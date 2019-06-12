Distribute
==========

Runs the [Parser](/parser) on multiple machines in parallel. Distribute provisions machines
on ec-2 or azure, then processes chunks of your data on each machine, and
finally terminates the machines.

Before you begin, follow the instructions in [Setup](#setup) to install Distribute.

1.  Launch instances on ec-2 or azure.  **Note: For ec-2, the General Purpose instance type is recommended (e.g. `m3.2xlarge`); instace types with lower memory/core may cause parser to abort.**

    ```bash
    fab launch:cloud=ec2,num=1
    ```
    This will launch 1 instance on ec-2. It will also put status information
    about the launched instance into `.state`.

2.  Install dependencies on remote machines
    ```bash
    fab install > install.log
    ```

3. Copy chunks to remote machines, run parser on remote machines and collect results:
    ```bash
    time fab copy_parse_collect > parse.log
    ```
    Tip: You can schedule the remote machines to be terminated on task completion automatically; note though that if the `parse` operation fails, nodes may not terminate:
    ```bash
    time fab copy_parse_collect terminate > parse.log
    ```
    Tip: You can provide additional parameters to override defaults:
    ```bash
    time fab copy_parse_collect:input=test/input.json,batch_size=1000,parallelism=8,key_id='item_id',content_id='content' > parse.log
    ```
    If `batch_size` is left unspecified, it will be computed automatically.  Note that very large batch sizes may cause memory errors.  See [Parser](/parser) documentation for details on parser parameters. *Note also that commas need to be backslash-escaped when passed in as parameters.*
    
4.  To check global status of distributed parse, run:
    ```bash
    fab get_status
    ```

5.  If not automatically terminated as above, or if error occured, terminate remote machines:
    ```bash
    fab terminate
    ```
    If termination is successful, the status information in `.state` will be deleted.

Your parsed information should now be available as a tsv file named `result` in your working directory.

## Setup

### Dependencies

If you have sudo rights, run `./setup.sh`.

If you don't have sudo rights, follow these steps instead. These have been tested on raiders3 (Stanford):
```
cd bazaar
wget https://raw.githubusercontent.com/pypa/virtualenv/develop/virtualenv.py
python virtualenv.py env --no-setuptools
source env/bin/activate
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
pip install fabric
pip install urltools
pip install azure
pip install botocore
```

The fab command line tool should work now.

Note that you will have to run `source env/bin/activate` after each login to initialize the environment.

### Generate SSH Keys 

Now, generate SSH keys.
```
./generate-keys.sh
```

### Build

Finally, create a self-extracting installer that will be run on worker nodes.
```
cd installer
./build 
cd ..
```

### Set EC2 or Azure credentials

See variables in `env_local.sh` and override as needed.

For ec2, we recommend storing credentials at `~/.aws/credentials` following this 
[documentation](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).
Make sure to `chmod 400 ~/.aws/credentials` and insert your access key and secret key:

```
[default]
aws_access_key_id = 
aws_secret_access_key = 
```

For azure, upload `ssh/mycert.cer` to the management portal via the "Upload" action of the "Settings" tab, and set the following variable in `env_local.sh`:
```
export AZURE_SUBSCRIPTION_ID=
```

## Tips

*  You can log into any of the launched nodes on ec-2 or azure:
   ```
   ssh -i ssh/bazaar.key -p PORT USER@HOST
   ```
   where USER, HOST, PORT are contained in `.state/HOSTS`.

*  You can choose different instance types (see `env_local.sh`).

*  Test your distribution setup on smaller samples of your data,
   and more basic instance types (eg. Standard_D2 for azure).
   Then, when you are confident that everything works as expected,
   choose a more powerful instance type (eg. Standard_D14 on azure),
   and increase the parallelism in step 4 above (eg. 8 or 16).

*  By default, Azure only allows you to use a maximum of 20 cores
   in total. This means you can not launch more than one instance
   of type Standard_D14 (16 cores) at a time. You can submit a
   request to Microsoft to increase your quota of cores.

*  In case of errors, make sure you stop running VMs through the
   Azure management portal or AWS management console. You may have
   to `rm -r .state` to continue using Distribute.
