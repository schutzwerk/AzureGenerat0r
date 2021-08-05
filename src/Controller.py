import json, os, re, copy, yaml, multiprocessing, random, glob, paramiko

from src.Model import Configuration, Specification
from deepmerge import Merger
from deepmerge.strategy.core import StrategyList
from deepmerge.strategy.list import ListStrategies
from deepmerge.strategy.dict import DictStrategies
from pathlib import Path
from importlib import import_module

'''
Data is processed as follows
Mapper -> Pluginer -> Connecter -> Predeployer -> Deployer -> Enricher 
'''

class Mapper:
    '''
    adds default values / resources
    '''

    def strategy_index_merging(config, path, base, nxt):
        return list(map(lambda b, n: {**n, **b}, base, nxt))

    def process(data):
        # adding strategy index_merging to merger
        ListStrategies.strategy_index_merging = Mapper.strategy_index_merging
        merger = Merger([(list, ['index_merging']), (dict, ['merge'])], ['use_existing'], ['use_existing'])

        innerMappings = [
            {'resource': 'virtual_network', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location},
            {'resource': 'subnet', 'resource_group_name': Configuration.resource_group},
            {'resource': 'container_registry', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location},
            {'resource': 'linux_virtual_machine', 'admin_username': Configuration.user, 'admin_password': Configuration.password, 'size': Configuration.vm_size, 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'admin_ssh_key' : { 'username' : Configuration.user, 'public_key' : Configuration.ssh_key_public}, 'os_disk' : {'caching': 'ReadWrite', 'storage_account_type': 'Standard_LRS'}, 'source_image_reference': {'publisher': 'Canonical', 'offer': 'UbuntuServer', 'sku': '16.04-LTS', 'version' : 'latest'}},
            {'resource': 'windows_virtual_machine', 'admin_username': Configuration.user, 'admin_password': Configuration.password, 'size': Configuration.vm_size, 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'os_disk' : {'caching': 'ReadWrite', 'storage_account_type': 'Standard_LRS'}, 'source_image_reference': {'publisher': 'MicrosoftWindowsServer', 'offer': 'WindowsServer', 'sku': '2016-Datacenter', 'version' : 'latest'}, 'winrm_listener': {'protocol': 'Http'}},
            {'resource': 'network_interface', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location},
            {'resource': 'public_ip', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'allocation_method': 'Dynamic'},
            {'resource': 'storage_account', 'name': 'uniquestorageaccname1337', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'account_tier': 'Standard', 'account_replication_type': 'LRS'},
            {'resource': 'mysql_server', 'name': 'uniquemysqlservername1337', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'sku_name': 'B_Gen5_2', 'version': '5.7', 'storage_mb': 5120},
            {'resource': 'mysql_firewall_rule', 'resource_group_name': Configuration.resource_group},
            {'resource': 'mysql_database', 'resource_group_name': Configuration.resource_group, 'charset': 'utf8', 'collation': 'utf8_unicode_ci'},
            {'resource': 'key_vault', 'resource_group_name': Configuration.resource_group, 'location': Configuration.location, 'tenant_id': Configuration.tenant_id, 'sku_name': 'standard'},
            {'resource': 'key_vault_access_policy', 'tenant_id': Configuration.tenant_id}
        ]


        outerMappings = [
            {'resource': 'windows_virtual_machine', 'create': 'virtual_machine_extension', 'name': 'script', 'virtual_machine_id': Connecter.DUMMY + '.id', 'publisher': 'Microsoft.Compute', 'type': 'CustomScriptExtension', 'type_handler_version': '1.9', 'settings': '{"fileUris": ["https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"]}', 'protected_settings': '{"commandToExecute": "powershell.exe -executionpolicy Unrestricted -file ./ConfigureRemotingForAnsible.ps1 -ForceNewSSLCert"}'}
        ]

        for m in innerMappings:
            for r in data:
                if (r['resource'] == m['resource']):
                    merger.merge(r, m)

        for m in outerMappings:
            id = 0
            for r in data:
                if (r['resource'] == m['resource']):
                    new_resource = merger.merge({}, m)
                    new_resource['resource'] = new_resource.pop('create')
                    new_resource = yaml.load(str(new_resource).replace(Connecter.DUMMY, Connecter.SIGNALWORD + str(id)))
                    data.append(new_resource)
                id += 1

class Pluginer:
    '''
    processes plugins
    '''

    SIGNALWORD = 'PLUGIN/'
    PATTERN = 'PLUGIN/[A-Za-z0-9_]+'
    def process(data):
        '''
        process the plugins from the specification by looking for the string PLUGIN/<pluginToStart>.
        starts the plugin and mounts the return value into the data model.
        '''

        os.chdir('../plugins')
        # execute plugins
        data_string = str(data)
        matches = re.findall(Pluginer.PATTERN, data_string)
        for m in matches:
            plugin_name = 'plugins.%s' % m.split("/")[1]
            result = import_module(plugin_name).main()
            data_string = data_string.replace(m, result, 1)
            Specification.data = yaml.load(data_string)
        Specification.data_enricher = yaml.load(data_string)
        os.chdir('../src')

class Connecter:
    '''
    connects resources by id and attribute
    '''

    SIGNALWORD = 'CONNECT/'
    DUMMY = 'CONNECT/0'
    PATTERN = 'CONNECT\/\d+.[\w\[\].]+'
    CONNECT_TEMPLATE = "${%s.r%s.%s}" #azuregenerator namespace: transform(resource).resource + id.attribute
    # create relationsships in mapping AzureGenerat0r namespace to Terraform namespace

    def transform_connection(resource, id, attribute):
        return Connecter.CONNECT_TEMPLATE % (Predeployer.transform_resource(resource), id, attribute)

    def process(data):
        data_string = str(data)
        matches = re.findall(Connecter.PATTERN, data_string)
        for m in matches:
            id, attribute = m.replace(Connecter.SIGNALWORD, "").split(".", 1)
            resource = data[int(id)]['resource']
            data_string = data_string.replace(m, Connecter.transform_connection(resource, id, attribute))
        Specification.data = yaml.load(data_string)

class Predeployer:
    '''
    transforms yaml resources to json resources
    adds arm and ad prefixes
    adds output variable for ip addresses
    '''

    azure_ad = ["user", "group", "service_principal", "domain", "application"]

    def transform_resource(key):
        if key in Predeployer.azure_ad:
            return 'azuread_' + key
        else:
            return 'azurerm_' + key

    def untransform_resource(key):
        if key in Predeployer.azure_ad:
            return key.replace('azuread_', '')
        else:
            return key.replace('azurerm_', '')

    def process(data):
        resources = []
        outputs = []
        id = 0
        for r in data:
            resource_ = Predeployer.transform_resource(r['resource'])
            name = 'r' + str(id)
            # dot because of similartiy to virtual_machine_extension
            if 'windows_virtual_machine' in resource_ or 'linux_virtual_machine' in resource_:
                outputs.append([str(id), Connecter.CONNECT_TEMPLATE %(resource_, id, "public_ip_address"), Connecter.CONNECT_TEMPLATE %(resource_, id, "private_ip_address"), Connecter.CONNECT_TEMPLATE %(resource_, id, "source_image_reference[0].offer")])

            r.pop('resource')
            r.pop('playbooks', None)
            r.pop('delayed', None)
            resources.append({
                    resource_ : {
                        name   : {
                            **r
                        }
                    }
                }
            )
            id += 1

        template = {
            "provider": {
                "azurerm": {
                    "subscription_id": Configuration.subscription_id,
                    "client_id": Configuration.app_id,
                    "client_secret": Configuration.client_secret,
                    "tenant_id": Configuration.tenant_id,
                    "version": Configuration.azure_rm_version,
                    "features": {}
                },
                "azuread": {
                    "version": Configuration.azure_ad_version
                }
            },
            "resource": resources,
            "output": {
                "vm_infos": {
                    "value": outputs
                }
            }
        }
        Specification.data = template


class Deployer:
    '''
    dumps model to tf file
    '''

    def process(data):
        # create file
        open('main.tf.json', 'w').close()
        f = open('main.tf.json', 'w')
        f.write(json.dumps(data, indent=2, separators=(',', ':')))
        f.close()

        # initialize Terraform
        os.system('terraform init 1> /dev/null')
        print(os.system('terraform plan'))
        apply = input('Do you want to apply this? y | n \n')
        if (apply == 'y'):
            os.system('terraform apply -auto-approve')
            os.system('terraform refresh > /dev/null')
            os.system('terraform output -json > ip_list.txt')
        else:
            return        

class Enricher:
    '''
    contains all functions used to deploy playbooks to virtual machines
    '''

    ips = []

    def create_inventory_for_windows(ip):
        '''
        Creates an inventory for ansible.
        :param user: user to access the machine
        :return: an ansible valid inventory containing credentials to access windows machines via WinRM
        '''

        template = "[windows]\n%s\n[windows:vars]\nansible_user=%s\nansible_password=%s\nansible_port=5986\nansible_connection=winrm\nansible_winrm_server_cert_validation=ignore"
        return template % (ip, Configuration.user, Configuration.password)


    def create_inventory_for_linux(ip):
        '''
        Creates an inventory for ansible.
        :param ip: ip of the target machine
        :param user: user to access the machine
        :return: an ansible valid inventory containing credentials to access linux machines via ssh.
        '''

        template = "[linux]\n%s\n[linux:vars]\nansible_user=%s\nansible_ssh_private_key_file=%s"
        return template % (ip, Configuration.user, Configuration.ssh_key_private_file)

    def read_ips():
        '''
        reads the public IPs from the ip_list.txt file using regex and writes them back to the model.
        These public IPs can be used by ansible to access the virtual machines.
        '''
        
        Enricher.ips = json.load(open('ip_list.txt', 'r'))['vm_infos']['value']


    def find_fitting_playbook(vm, playbook):
        '''
        this method is getting called if no path for a playbook has been specified. This means the user want AzureGenerat0r to select a random playbook based on a type and/or properties.
        this method searches for a playbook fitting the specified requirements.
        :param vm: virtual machine for which the playbook will be applied.
        :param playbook: playbook object containing the constraints from the specification.
        :return: path to the playbook as string <OS>/<Type>/<Playbook> or None if no fitting playbook as been found.
        '''
        
        os_str = "linux" if vm["resource"] in "linux_virtual_machine" else "windows"
        playbook_type = playbook.get("type") if playbook.get("type") else random.choice(["packages", "vulnerability", "config", "service"])
        if playbook.get("properties"):
            # find fitting playbook
            fitting_playbooks = []
            for playbook_dir in os.listdir("../playbooks/%s/%s" % (os_str, playbook_type)):
                f = open("../playbooks/%s/%s/%s/metadata.yml" % (os_str, playbook_type, playbook_dir))
                metadata = yaml.load(f.read())
                if all(item in metadata.items() for item in playbook.get("properties").items()):
                    fitting_playbooks.append(playbook_dir)
            if fitting_playbooks:
                result_playbook = random.choice(fitting_playbooks)
            else:
                return None
        else:
            # choose random playbook without properties
            result_playbook = random.choice(os.listdir("../playbooks/%s/%s" % (os_str, playbook_type)))
        return "%s/%s/%s" % (os_str, playbook_type, result_playbook)

    def enrich_vm(vm, ip, id, job_id):
        '''
        applies a playbook to a virtual machine. check if a vm has to be accessed via ssh (for linux) or via winRM (for windows).

        :param vm: vm to apply the playbook
        :param ip: ip of the vm
        :param jobID: jobID used to keep track of multithreaded processes
        '''

        job_id = str(job_id)
        inventory = Enricher.create_inventory_for_linux(ip) if vm.get("resource") in "linux_virtual_machine" else Enricher.create_inventory_for_windows(ip)
        f = open('../ansible/hosts' + job_id, 'w+')
        f.write(inventory)
        f.close()

        # run specified ansible playbook with commandLine arguments. Arguments passed as json.
        print('Begin Enrichement of machine: ' + ip)
        playbook_number = 0
        for playbook in vm.get("playbooks"):
            if playbook.get("path"):
                path = playbook.get("path")
            else:
                path = Enricher.find_fitting_playbook(vm, playbook)
                print("randomized selection choosed " + str(path) + " for " + ip)
            if path:
                args = json.dumps(playbook.get("args"))
                cmdFormat = 'ansible-playbook -i ../ansible/hosts%s ../playbooks/%s/main.yml 1> ../ansible/output%s%s.txt --extra-vars \'%s\''
                cmd = cmdFormat % (job_id, path, job_id, playbook_number, args)
                os.system(cmd)
            playbook_number += 1
        print('Enrichment of machine ' + ip + ' completed')

    def process(data):
        '''
        iterates the model searching for playbooks and starts the enrichment process for each vm with a own thread.
        by reading the delayed attribute it seperates the enrichment process into two stages. This can be
        used by users to overcome time based dependencies when enriching a machine.
        '''

        # cleanup
        for file in glob.glob('../ansible/*'):
            os.remove(file)

        # ips from deployment
        Enricher.read_ips()

        # stage 1 enrichment
        jobs = []
        jobID = 0
        for ip in Enricher.ips:
            id = int(ip[0])
            vm = data[id]
            if vm.get("playbooks") and not vm.get("delayed"):
                process = multiprocessing.Process(target=Enricher.enrich_vm, args=(vm, ip[1], ip[0], jobID))
                jobs.append(process)
            jobID += 1
        for j in jobs:
            j.start()

        for j in jobs:
            j.join()
            
        # stage 2 enrichment
        jobs = []
        jobID = 0
        for ip in Enricher.ips:
            id = int(ip[0])
            vm = data[id]
            if vm.get("playbooks") and vm.get("delayed"):
                process = multiprocessing.Process(target=Enricher.enrich_vm, args=(vm, ip[1], ip[0], jobID))
                jobs.append(process)
            jobID += 1
        for j in jobs:
            j.start()

        for j in jobs:
            j.join()

        print('Enrichment completed')