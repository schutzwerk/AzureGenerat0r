import os
from pathlib import Path

config = """subscriptionID:
tenant_id:
app_id:
client_secret:
resource_group:
location:  # english name of the location, for example centralus.
ssh_key_private_file:
ssh_key_public_file:
ansible_host_key_checking: true
name_for_logging:
my_public_ip: none    # ports will be exposed to the internet
# password must fulfill Azure password requirements
user:
password:
# targeted azure version for terraform, do not change
azure_rm_version: =2.24.0
azure_ad_version: =1.0.0
# configuration options for azure virtual machines
storage_account_type: Standard_LRS
vm_size: Standard_DS1_V2
vm_os_version: latest
delete_os_disk_on_termination: true
data_storage_account_type: Standard_LRS """

spec = "# specify here. for example see specifications/repoExample"

def create_configuration_file():
    with open('../configuration.yml', 'w+') as outfile:
        outfile.write(config)
        outfile.close()

def create_specification_file():
    with open('../specification.yml', 'w+') as outfile:
        outfile.write(spec)
        outfile.close()

'''
creates configuration and specification files
'''
def setup():
    create_configuration_file()
    create_specification_file()
    Path("../ansible").mkdir(parents=True, exist_ok=True)
