import yaml
from src.Model import *
import copy


def parseConfiguration():
    '''
    parses the specification.yml file, extracts the data and creates the data model for Network.networkModel as an network object.
    :param specification: specification to read the data from
    '''
    with open("../configuration.yml", "r") as stream:
        data = yaml.load(stream)
        Configuration.subscriptionID = data['subscriptionID']
        Configuration.appID = data['appID']
        Configuration.clientSecret = data['clientSecret']
        Configuration.tenantID = data['tenantID']
        Configuration.resourceGroup = data['resourceGroup']
        Configuration.location = data['location']
        Configuration.sshKeyPrivate = data['sshKeyPrivateFile']
        Configuration.sshKeyPublic = data['sshKeyPublicFile']
        Configuration.terraformProviderVersion = data['terraformProviderVersion']
        Configuration.storageAccountType = data['storageAccountType']
        Configuration.vmSize = data['vmSize']
        Configuration.vmOsVersion = data['vmOsVersion']
        Configuration.deleteOsDiskOnTermination = data['deleteOsDiskOnTermination']
        Configuration.dataStorageAccountType = data['dataStorageAccountType']
        Configuration.password = data['password']
        Configuration.user = data['user']
        Configuration.nameForLogging = data['nameForLogging']
        stream.close()

def parseSpecification():
    '''
    parses the specification.yml file, extracts the data and creates the data model for Network.networkModel as an network object.
    :param specification: specification to read the data from
    '''
    specification='../specification.yml'
    with open(specification, "r") as stream:
        data = yaml.load(stream)
    try:
        publicIP = str(data['myPublicIP']).lower()
        if 'none' == publicIP:
            Network.myPublicIP = "*"
        else:
            Network.myPublicIP = publicIP
        network = data['network']
    except (KeyError, TypeError) as e:
        print("Your specification is invalid: " + str(e))
        exit(0)

    # default values are handled in exception blocks
    # each value that is read out is one try block because a big try block doesnt continue on the next command
    # if an exception is raised. better solution?

    networkObj = Network()
    for subnet in network:
        try:
            subnetPrefix = subnet['addressSpace']
        except (KeyError, TypeError):
            subnetPrefix = "10.0." + str(Network.subnetDefaultId) + ".0/24"
            Network.subnetDefaultId += 1

        try:
            mountTemplate = subnet['mountTemplate']
        except (KeyError, TypeError):
            mountTemplate = None

        try:
            routes = subnet['routes']
        except (KeyError, TypeError):
            routes = []

        routesObj = []
        for route in routes:
            routeObj = Route(route[0], route[1], route[2])
            routesObj.append(routeObj)

        subnetVms = []
        try:
            vms = subnet['vms']
        except (KeyError, TypeError):
            vms = []

        for vm in vms:

            try:
                counter = int(vm['counter'])
            except (KeyError, TypeError):
                counter = 1

            for i in range(0, counter):
                vmObj = VM()

                try:
                    vmObj.system = vm['system']
                except (KeyError, TypeError):
                    vmObj.system = 'UbuntuServer'

                try:
                    vmObj.delayedEnrichment = vm['delayedEnrichment']
                except (KeyError, TypeError):
                    vmObj.delayedEnrichment = False

                try:
                    vmObj.mountTemplate = vm['mountTemplate']
                except (KeyError, TypeError):
                    vmObj.mountTemplate = None

                try:
                    modules = vm['modules']
                except (KeyError, TypeError):
                    modules = []

                moduleObjects = []
                for module in modules:
                    moduleObj = Module()

                    try:
                        moduleObj.path = module['path']
                    except (KeyError, TypeError):
                        moduleObj.path = None

                    try:
                        moduleObj.type = module['type']
                    except (KeyError, TypeError):
                        moduleObj.type = None

                    try:
                        args = copy.deepcopy(module['args'])  # deepcopy creates new reference to dict
                    except (KeyError, TypeError):
                        args = {}
                    moduleObj.args = args

                    try:
                        properties = copy.deepcopy(module['properties'])
                    except (KeyError, TypeError):
                        properties = {}
                    moduleObj.properties = properties

                    moduleObjects.append(moduleObj)
                vmObj.modules = moduleObjects

                try:
                    interfaces = vm['interfaces']
                except (KeyError, TypeError):
                    interfaces = []
                interfacesObjects = []
                for interface in interfaces:
                    interfacesObjects.append(Interface(interface[0], interface[1], interface[2]))

                vmObj.interfaces = interfacesObjects

                Network.numberOfVms += 1
                subnetVms.append(vmObj)
        subnetObj = Subnet(Network.numberOfSubnets, subnetPrefix, vms=subnetVms, routes=routesObj,
                           mountTemplate=mountTemplate)
        networkObj.addSubnet(subnetObj)
        Network.numberOfSubnets += 1
    Network.networkModel = networkObj
