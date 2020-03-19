import os
import re
from terrascript import *
from src import Parser
from src.Preprocessor import *
from src.Model import Network
from AzureGenerat0r import *

'''
contains all functions used to create the specified infrastructure like Subnets, VMs, Routetables,...
'''


def deployInfrastructure():
    '''
    deploys the infrastructure in Azure by using Terraform and the (on runtime created) terraform configuration in main.tf.
    returns an list of public IPs that can be used from VmEnricher resp. from Ansible to access the VMs.
    '''
    # initialize Terraform
    os.system('terraform init 1> /dev/null')
    print(os.system('terraform plan'))
    apply = input('Do you want to apply this? y | n \n')
    if (apply == 'y'):
        os.system('terraform apply -auto-approve')
        os.system('terraform refresh > /dev/null')
        os.system('terraform output')
        os.system('terraform output > ipListForAnsible.txt')
    else:
        readCommands()


def createTerraformConfig():
    '''
    creates the terraform configuration main.tf that contains all the resources that should be deployed.
    the configuration is created by reading the model and using Terrascript to create a valid configuration file for terraform. (https://github.com/mjuenema/python-terrascript)
    this method also reads the credentials.yml file that contains user information needed for terraform to access Azure.
    the ${..} syntax is part of terraform syntax.
    '''

    networkModel = Network.networkModel
    resourceGroupName = Configuration.resourceGroup
    location = Configuration.location
    sshKeyPublic = Configuration.sshKeyPublic
    userprefix = Configuration.nameForLogging + '-'

    # create config
    ts = Terrascript()
    ts += provider('azurerm',
                   subscription_id=Configuration.subscriptionID,
                   client_id=Configuration.appID,
                   client_secret=Configuration.clientSecret,
                   tenant_id=Configuration.tenantID, version=Configuration.terraformProviderVersion)

    subnetIndex = 0
    vmIndex = 0
    for subnet in networkModel.subnets:
        for vm in subnet.vms:
            publicIpDnsNames = ['linsimplevmip-' + str(vmIndex)]

            if vm.hasInterface():
                nicsSubnetIds = list(
                    map(lambda x: '${module.vnet.vnet_subnets[' + str(x.subnetID) + ']}', vm.interfaces))
                nicsAllocType = list(
                    map(lambda x: x.allocationType, vm.interfaces))
                nicsPrivIp = list(map(lambda x: x.privateIP, vm.interfaces))
            else:
                # create default interface
                nicsSubnetIds = ['${module.vnet.vnet_subnets[' + str(subnet.id) + ']}']
                nicsAllocType = ['dynamic']
                nicsPrivIp = ['']

            ts += module(vm.system + 'servers' + str(vmIndex),
                         source='terraform-azurerm-vm',
                         resource_group_name=resourceGroupName,
                         vm_hostname='myVM-' + str(vmIndex),
                         location=location,
                         ssh_key=sshKeyPublic,
                         vm_os_simple=vm.system,
                         public_ip_dns=publicIpDnsNames,
                         number_NICs=len(nicsSubnetIds),
                         nics_subnet_ids=nicsSubnetIds,
                         nics_alloc_type=nicsAllocType,
                         nics_priv_ip=nicsPrivIp,
                         storage_account_type=Configuration.storageAccountType,
                         vm_size=Configuration.vmSize,
                         vm_os_version=Configuration.vmOsVersion,
                         delete_os_disk_on_termination=Configuration.deleteOsDiskOnTermination,
                         data_sa_type=Configuration.dataStorageAccountType,
                         admin_username=Configuration.user,
                         admin_password=Configuration.password)

            ts += output('VM-' + str(vmIndex),
                         value=['${module.' + vm.system + 'servers' + str(vmIndex) + '.vm_os_simple}',
                                '${module.' + vm.system + 'servers' + str(vmIndex) + '.public_ip_address}',
                                '${module.' + vm.system + 'servers' + str(vmIndex) + '.network_interface_private_ip}'])
            vmIndex += 1

        routePrefixes = list(map(lambda x: x.routePrefix, subnet.routes))
        routeNextHopTypes = list(map(lambda x: x.nextHopType, subnet.routes))
        routeNextHopIPs = list(map(lambda x: x.nextHopIp, subnet.routes))
        routeNames = list(map(lambda x: "Route" + str(x + 1), range(0, len(subnet.routes))))

        ts += module('routetable' + str(subnetIndex),
                     source='terraform-azurerm-routetable',
                     location=location,
                     resource_group_name=resourceGroupName,
                     route_table_name="routeTableForSubnet" + str(subnetIndex + 1),
                     route_prefixes=routePrefixes,
                     route_nexthop_types=routeNextHopTypes,
                     route_next_hop_ip_address=routeNextHopIPs,
                     route_names=routeNames)

        subnetIndex += 1

    # create subnets
    subnetNames = list(map(lambda x: "subnet" + str(x.id), networkModel.subnets))
    subnetPrefix = list(map(lambda x: x.subnetPrefix, networkModel.subnets))
    routeTableIds = list(
        map(lambda x: '${module.routetable' + str(x) + '.routetable_id}', range(0, len(networkModel.subnets))))

    ts += module('vnet', source="terraform-azurerm-vnet",
                 vnet_name=userprefix + 'vnet',
                 version="~> 1.0.0",
                 location=location,
                 subnet_names=subnetNames,
                 subnet_prefixes=subnetPrefix,
                 resource_group_name=resourceGroupName,
                 route_table_ids=routeTableIds,
                 own_IP_Address=Network.myPublicIP
                 )

    # erases file
    f = open('main.tf', 'w').close()
    # write config to file
    f = open('main.tf', 'w')
    f.write(ts.dump())


def main():
    createTerraformConfig()
    deployInfrastructure()
