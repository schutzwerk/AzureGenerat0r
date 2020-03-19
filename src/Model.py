'''
contains the model used by AzureGenerat0r.
It is a hierarchical structured model:
a network knows a set of subnets
a subnet knows a set of virtual machines and a set of routes
a virtual machine knows a set of modules and a set of interfaces
a interface belongs to one subnet specified by an ID.
'''

class Configuration:
    subscriptionID = None
    appID = None
    clientSecret = None
    tenantID = None
    resourceGroup = None
    location = None
    sshKeyPrivate = None
    sshKeyPublic = None
    terraformProviderVersion = None
    storageAccountType = None
    vmSize = None
    vmOsVersion = None
    deleteOsDiskOnTermination = None
    dataStorageAccountType = None
    user = None
    password = None
    nameForLogging = None

class Network:
    '''
    static variables that can be accessed from anywhere including networkModel, the only network object created.
    '''

    numberOfVms = 0
    numberOfSubnets = 0
    subnetDefaultId = 1
    myPublicIP = None
    resourceGroupName = None
    location = None
    networkModel = None

    def __init__(self, subnets=None):
        '''
        :param subnets: subnets a network knows
        '''

        if subnets is None:
            self.subnets = []
        else:
            self.subnets = subnets

    def addSubnet(self, subnet):
        '''
        adds a subnet to the network
        :param subnet: subnet to add
        '''

        self.subnets.append(subnet)

    def getVMs(self):
        '''
        returns all VMs of the network by iterating all subnets
        :return: VMs contained in the network
        '''

        vms = []
        for subnet in self.subnets:
            for vm in subnet.vms:
                vms.append(vm)
        return vms

    def __repr__(self):
        '''
        returns a string representation of the current network
        :return: string representation
        '''

        return str(self.__dict__)


class Subnet:
    def __init__(self, id, subnetPrefix, vms=[], routes=[], mountTemplate=None):
        '''
        :param id: id of the subnet. The first specified subnet from the specification has ID 0. This ID has to be referenced if you want to specify a network interface for a specific subnet.
        :param subnetPrefix: address prefix in CIDR notation.
        :param vms: vms that are part of the subnet.
        :param routes: routing configuration for the subnet.
        :param mountTemplate: string containing a path to a subnet, that should be mounted.
        '''

        self.vms = vms
        self.id = id
        self.subnetPrefix = subnetPrefix
        self.routes = routes
        self.mountTemplate = mountTemplate

    def hasMount(self):
        return bool(self.mountTemplate)

    def addVM(self, vm):
        self.vms.append(vm)

    def __repr__(self):
        return str(self.__dict__)


class VM:
    def __init__(self, system='linux', modules=[], interfaces=[], delayedEnrichment=False, mountTemplate=None):
        '''
        :param system: operation system the VM will have
        :param modules: modules that will be deployed to the VMs
        :param interfaces: interfaces a virtual machine has
        :param delayedEnrichment: if true => modules are applied delayed (in a second deployment stage)
        :param mountTemplate: string containing a path to a virtual machine, that should be mounted
        '''

        self.system = system
        self.modules = modules
        self.interfaces = interfaces
        self.delayedEnrichment = delayedEnrichment
        self.mountTemplate = mountTemplate
        self.publicIP = None

    def __repr__(self):
        return str(self.__dict__)

    def isLinux(self):
        if self.system == 'WindowsServer':
            return False
        else:
            return True

    def hasInterface(self):
        if self.interfaces:
            return True
        else:
            return False

    def hasModule(self):
        if self.modules:
            return True
        else:
            return False

    def hasMount(self):
        return bool(self.mountTemplate)


class Module:
    def __init__(self, path=None, properties=None, args=None, type=None):
        '''
        :param path: path of the module that should be applied to the vm.
        :param properties: properties used to filter modules when no specific module is specified via path
        :param args: arguments for a module
        :param type: type of a module used to filter when no specific module is specified via path
        '''

        self.path = path
        self.properties = properties
        self.args = args
        self.type = type

    def hasPath(self):
        if self.path is None:
            return False
        else:
            return True

    def hasType(self):
        if self.type is None:
            return False
        else:
            return True

    def hasMount(self):
        return bool(self.mountTemplate)

    def hasProperties(self):
        return bool(self.properties)

    def __repr__(self):
        return str(self.__dict__)


class Route:
    def __init__(self, routePrefix="", nextHopType="", nextHopIP=""):
        '''
        :param routePrefix: address prefix a incoming packet is checked against
        :param nextHopType: defines next hop type of the packet (https://www.terraform.io/docs/providers/azurerm/r/route_table.html#next_hop_type)
        :param nextHopIP: defines ip of the next hop
        '''
        self.routePrefix = routePrefix
        self.nextHopType = nextHopType
        self.nextHopIp = nextHopIP

    def __repr__(self):
        return str(self.__dict__)


class Interface:
    def __init__(self, subnetID="", allocationType="", privateIP=""):
        '''
        :param subnetID: subnet ID a interface belongs to.
        :param allocationType: static or dynamic ip address allocation
        :param privateIP: if allocationType=static => use the specified private ip address
        '''
        self.subnetID = subnetID
        self.allocationType = allocationType
        self.privateIP = privateIP

    def __repr__(self):
        return str(self.__dict__)
