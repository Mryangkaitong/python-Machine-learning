#!/usr/bin/env python

from azure import *
from azure.servicemanagement import *
import errno
import getopt
import os
import shutil
import subprocess
import sys
import time

# read env_local.sh
def source_env_local():
    command = ['bash', '-c', 'source env_local.sh && env']
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.rstrip().partition("=")
        os.environ[key] = value
    proc.communicate()

source_env_local()

# make sure we have required parameters
AZURE_SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID')
if not AZURE_SUBSCRIPTION_ID:
    print('AZURE_SUBSCRIPTION_ID is not set.')
    exit(1)

AZURE_SERVICE_NAME = os.environ.get('AZURE_SERVICE_NAME')
if not AZURE_SERVICE_NAME:
    print('AZURE_SERVICE_NAME is not set.')
    exit(1)

AZURE_ROLE_SIZE = os.environ.get('AZURE_ROLE_SIZE')
if not AZURE_ROLE_SIZE:
    print('AZURE_ROLE_SIZE is not set.')
    exit(1)

AZURE_STORAGE_ACCOUNT = os.environ.get('AZURE_STORAGE_ACCOUNT')
if not AZURE_STORAGE_ACCOUNT:
    print('AZURE_STORAGE_ACCOUNT is not set.')
    exit(1)

# management certificate
AZURE_MGMT_CERT = 'ssh/mycert.pem'

# service certificate
AZURE_SERVICE_PEM = 'ssh/bazaar.pem'

# vm settings
linux_image_name = 'b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_2_LTS-amd64-server-20150309-en-us-30GB'
container_name = 'bazaarctr'
location = 'West US'

class AzureClient:

    def __init__(self):
        self.sms = ServiceManagementService(AZURE_SUBSCRIPTION_ID, AZURE_MGMT_CERT)

    def service_exists(self):
        try:
            props = self.sms.get_hosted_service_properties(AZURE_SERVICE_NAME)
            return props is not None
        except:
            return False

    def create_hosted_service(self):
        if not self.service_exists():
            print('Creating service ' + AZURE_SERVICE_NAME) 
            result = self.sms.create_hosted_service(
                AZURE_SERVICE_NAME,
                AZURE_SERVICE_NAME + 'label',
                AZURE_SERVICE_NAME + 'description',
                location)
            self._wait_for_async(result.request_id)
            self.create_service_certificate()

    def list_services(self):
        result = self.sms.list_hosted_services()
        for hosted_service in result:
            print('- Service name: ' + hosted_service.service_name)
            print('  Management URL: ' + hosted_service.url)
            print('  Location: ' + hosted_service.hosted_service_properties.location)

    def delete_service():
        self.sms.delete_hosted_service(AZURE_SERVICE_NAME)

    def delete_deployment():
        self.sms.delete_deployment('myhostedservice', 'v1')

    def _linux_role(self, role_name, subnet_name=None, port='22'):
        container_name = 'bazaarctr' + role_name
        host_name = 'hn' + role_name
        system = self._linux_config(host_name)
        os_hd = self._os_hd(linux_image_name,
			container_name,
			role_name + '.vhd')
        network = self._network_config(subnet_name, port)
        return (system, os_hd, network)

    def get_fingerprint(self):
        import hashlib
        with open (AZURE_SERVICE_PEM, "r") as myfile:
           data = myfile.readlines()
        lines = data[1:-1]
        all = ''.join([x.rstrip() for x in lines])
        key = base64.b64decode(all.encode('ascii'))
        fp = hashlib.sha1(key).hexdigest()
        return fp.upper()

    def _linux_config(self, hostname):
        SERVICE_CERT_THUMBPRINT = self.get_fingerprint() 
        pk = PublicKey(SERVICE_CERT_THUMBPRINT, '/home/bazaar/.ssh/authorized_keys')
        pair = KeyPair(SERVICE_CERT_THUMBPRINT, '/home/bazaar/.ssh/id_rsa')
        system = LinuxConfigurationSet(hostname, 'bazaar', 'u7;9jbp!', True)
        system.ssh.public_keys.public_keys.append(pk)
        system.ssh.key_pairs.key_pairs.append(pair)
        system.disable_ssh_password_authentication = True 
        return system

    def _network_config(self, subnet_name=None, port='22'):
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        network.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint('SSH', 'tcp', port, '22'))
        if subnet_name:
            network.subnet_names.append(subnet_name)
        return network

    def _os_hd(self, image_name, target_container_name, target_blob_name):
        media_link = self._make_blob_url(
            AZURE_STORAGE_ACCOUNT, 
            target_container_name, target_blob_name)
        os_hd = OSVirtualHardDisk(image_name, media_link,
            disk_label=target_blob_name)
        return os_hd

    def _make_blob_url(self, storage_account_name, container_name, blob_name):
        return 'http://{0}.blob.core.windows.net/{1}/{2}'.format(
            storage_account_name, container_name, blob_name)

    def create_storage(self):
        name = AZURE_STORAGE_ACCOUNT 
        label = 'mystorageaccount'
        location = 'West US'
        desc = 'My storage account description.'

        result = self.sms.create_storage_account(name, desc, label, location=location)

        self._wait_for_async(result.request_id)

    def storage_account_exists(self, name):
        try:
            props = self.sms.get_storage_account_properties(name)
            return props is not None
        except:
            return False

    def list_storage(self):
        result = self.sms.list_storage_accounts()
        for account in result:
            print('Service name: ' + account.service_name)
            print('Location: ' + account.storage_service_properties.location)
            print('')

    def delete_storage(self):
        self.sms.delete_storage_account(AZURE_STORAGE_ACCOUNT)

    def list_role_sizes(self):
        result = self.sms.list_role_sizes()
        for rs in result:
            print('Name: ' + rs.name)

    def _wait_for_async(self, request_id):
        try:
           self.sms.wait_for_operation_status(request_id, timeout=600)
        except azure.WindowsAzureAsyncOperationError as e:
           from pprint import pprint
           pprint (vars(e.result.error))

    def _wait_for_deployment(self, service_name, deployment_name,
    			  status='Running'):
       count = 0
       props = self.sms.get_deployment_by_name(service_name, deployment_name)
       while props.status != status:
          count = count + 1
          if count > 120:
             self.assertTrue(
                False, 'Timed out waiting for deployment status.')
          time.sleep(5)
          props = self.sms.get_deployment_by_name(
             service_name, deployment_name)

    def _wait_for_role(self, service_name, deployment_name, role_instance_name,
                      status='ReadyRole'):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while self._get_role_instance_status(props, role_instance_name) != status:
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False, 'Timed out waiting for role instance status.')
            time.sleep(5)
            props = self.sms.get_deployment_by_name(
                service_name, deployment_name)

    def _get_role_instance_status(self, deployment, role_instance_name):
        for role_instance in deployment.role_instance_list:
            if role_instance.instance_name == role_instance_name:
                return role_instance.instance_status
        return None

    def delete_hosted_service(self):
        print('Terminating service')
        try:
            self.sms.delete_hosted_service(AZURE_SERVICE_NAME, complete=True)
        except:
            pass
        if os.path.exists('.state'):
            shutil.rmtree('.state')

    def create_state_dir(self):
        try:
            os.makedirs('.state')
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir('.state'):
                print("Found existing .state dir. Please terminate instances first.")
                exit(1)
            else: raise

    def list_os_images_public(self):
        result = self.sms.list_os_images()
        for img in result:
            print(img.name)

    def create_service_certificate(self):
        with open(AZURE_SERVICE_PEM, "rb") as bfile:
            cert_data = base64.b64encode(bfile.read()).decode() 
            cert_format = 'pfx'
            cert_password = ''
            cert_res = self.sms.add_service_certificate(service_name=AZURE_SERVICE_NAME,
                data=cert_data,
                certificate_format=cert_format,
                password=cert_password)
        self._wait_for_async(cert_res.request_id)

    def create_deployment_and_roles(self, num_machines = 1):
        deployment_name = AZURE_SERVICE_NAME

        # one role for each machine
        roles = []
        for i in range(0, num_machines):
            roles.append(AZURE_SERVICE_NAME + str(i))

        system, os_hd, network = self._linux_role(roles[0], port='2000')

        result = self.sms.create_virtual_machine_deployment(
            AZURE_SERVICE_NAME, deployment_name, 'production',
            deployment_name + 'label', roles[0], system, os_hd,
            network, role_size=AZURE_ROLE_SIZE)

        self._wait_for_async(result.request_id)
        self._wait_for_deployment(AZURE_SERVICE_NAME, deployment_name)
        self._wait_for_role(AZURE_SERVICE_NAME, deployment_name, roles[0])

        for i in range(1, len(roles)):
            system, os_hd, network = self._linux_role(roles[i], port=str(2000+i))

            result = self.sms.add_role(AZURE_SERVICE_NAME, deployment_name, roles[i],
                system, os_hd, network, role_size=AZURE_ROLE_SIZE)
            self._wait_for_async(result.request_id)
            self._wait_for_role(AZURE_SERVICE_NAME, deployment_name, roles[i])
         
        # write to .state
        with open('.state/HOSTS', 'w') as f:
            for i in range(0, len(roles)):
                f.write('bazaar@' + AZURE_SERVICE_NAME + '.cloudapp.net:' + str(2000+i) + '\n')
        with open('.state/DIRS', 'w') as f:
            for i in range(0, len(roles)):
                f.write('/mnt\n')
        with open('.state/CLOUD', 'w') as f:
            f.write('azure')

def launch(argv):
    num_instances = 1
    try:
        opts, args = getopt.getopt(argv,"n:",[])
    except getopt.GetoptError:
        #print " -n <numinstances>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-n':
            num_instances = int(arg)
    print('Launching ' + str(num_instances) + ' instances on Azure')

    client = AzureClient()
    client.create_state_dir()
    client.create_hosted_service()
    if not client.storage_account_exists(AZURE_STORAGE_ACCOUNT):
        client.create_storage()
    client.create_deployment_and_roles(num_instances)

def terminate():
    client = AzureClient()
    client.delete_hosted_service()
    # We don't delete storage account, because it takes a long time to re-create.
    #client.delete_storage()

def usage():
    print("Usage: azure-client.py launch|terminate|role_sizes [OPTIONS]")
    exit(1)

def main(argv):
    if len(argv) < 1:
       usage()
    cmd = argv[0]
    if cmd == 'launch':
        launch(argv[1:])
    elif cmd == 'terminate':
        terminate()
    elif cmd == 'role_sizes':
        client = AzureClient()
        client.list_role_sizes()
    else:
        usage()

if __name__ == "__main__":
    main(sys.argv[1:])
