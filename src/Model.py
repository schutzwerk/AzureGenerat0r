import yaml

class Configuration:
    def init():
        with open("../configuration.yml", "r") as stream:
            data = yaml.load(stream)
            stream.close()
        Configuration.subscription_id = data['subscription_id']
        Configuration.app_id = data['app_id']
        Configuration.client_secret = data['client_secret']
        Configuration.tenant_id = data['tenant_id']
        Configuration.resource_group = data['resource_group']
        Configuration.location = data['location']
        Configuration.ssh_key_private_file = data['ssh_key_private_file']
        Configuration.ssh_key_public_file = data['ssh_key_public_file']
        Configuration.ansible_host_key_checking = data['ansible_host_key_checking']
        Configuration.azure_rm_version = data['azure_rm_version']
        Configuration.azure_ad_version = data['azure_ad_version']
        Configuration.storage_account_type = data['storage_account_type']
        Configuration.vm_size = data['vm_size']
        Configuration.vm_os_version = data['vm_os_version']
        Configuration.delete_os_disk_on_termination = data['delete_os_disk_on_termination']
        Configuration.data_storage_account_type = data['data_storage_account_type']
        Configuration.password = data['password']
        Configuration.user = data['user']
        Configuration.name_for_logging = data['name_for_logging']
        public_ip = str(data['my_public_ip']).lower()
        if 'none' == public_ip:
            Configuration.my_public_ip = "*"
        else:
            Configuration.my_public_ip = public_ip
        
        with open(Configuration.ssh_key_public_file,'r') as f:
            Configuration.ssh_key_public = f.read()
            f.close()

class Specification:
    data = None
    data_enricher = None

    def init():
        with open('../specification.yml', "r") as stream:
            Specification.data = Specification.data_enricher = yaml.load(stream)
            stream.close()