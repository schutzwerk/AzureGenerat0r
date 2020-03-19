from src.Parser import *
from src import Model
import os
import copy


def processTemplates():
    '''
    mounts templates from the specification into the model.
    '''

    re = True
    while re is True:
        re = False
        pivot = 0
        for subnet in Network.networkModel.subnets:
            if subnet.hasMount():
                subnetsToAdd = readSubnets(subnet.mountTemplate, pivot)
                Network.networkModel.subnets[pivot] = copy.deepcopy(subnetsToAdd[0])
                Network.networkModel.subnets[pivot + 1:pivot + 1] = subnetsToAdd[1:]
                re = True
                break
            else:
                pivot += 1

    id = 0
    for subnet in Network.networkModel.subnets:
        subnet.id = id
        id += 1

    # remove mount stubs
    for subnet in Network.networkModel.subnets:
        subnet.vms[:] = [x for x in subnet.vms if not x.hasMount()]

    # pivot and index stuff for keeping vm order
    for subnet in Network.networkModel.subnets:
        pivot = 0
        for vm in subnet.vms:
            if vm.hasMount():
                indexToInsertVM = 0
                for vmToAdd in readVM(vm.mountTemplate):
                    subnet.vms.insert(pivot + indexToInsertVM, vmToAdd)
                    try:
                        subnet.vms.remove(vm)
                    except (ValueError):
                        pass
                    indexToInsertVM += 1
            pivot += 1

    # remove mount vms
    for subnet in Network.networkModel.subnets:
        subnet.vms[:] = [x for x in subnet.vms if not x.hasMount()]

    # update number vms
    numberOfVMs = 0
    for subnet in Network.networkModel.subnets:
        for vm in subnet.vms:
            numberOfVMs += 1


def processPlugins():
    '''
    process the plugins from the specification by looking for the string PLUGIN/<pluginToStart>.
    starts the plugin and mounts the return value into the data model.
    '''

    # initialize plugins
    os.chdir('../plugins')
    module_files = filter(lambda x: x.endswith('.py'), os.listdir())
    for m in module_files:
        name = 'plugins.' + m[:-3]
        x = __import__(name, fromlist=[''])
        x.init()
    signalWord = "PLUGIN"
    for subnet in Network.networkModel.subnets:
        if str(subnet.id).__contains__(signalWord):
            subnet.id = os.popen('python3 ' + subnet.id.split("/")[1] + '.py').read().replace('\n', '').rem
        if str(subnet.subnetPrefix).__contains__(signalWord):
            subnet.subnetPrefix = os.popen(
                'python3 ' + subnet.subnetPrefix.split("/")[1] + '.py').read().replace('\n', '')

        for vm in subnet.vms:
            if str(vm.system).__contains__(signalWord):
                vm.system = os.popen('python3 ' + vm.system.split("/")[1] + '.py').read().replace('\n', '')
            if str(vm.delayedEnrichment).__contains__(signalWord):
                vm.delayedEnrichment = os.popen('python3 ' + vm.delayedEnrichment.split("/")[1] + '.py')
            for module in vm.modules:
                if str(module.path).__contains__(signalWord):
                    module.path = os.popen('python3 ' + module.path.split("/")[1] + '.py').read().replace(
                        '\n', '')
                if str(module.type).__contains__(signalWord):
                    module.type = os.popen('python3 ' + module.type.split("/")[1] + '.py').read().replace(
                        '\n', '')
                for key in module.args:  # HERE
                    if str(module.args[key]).__contains__(signalWord):
                        module.args[key] = os.popen('python3 ' + module.args[key].split("/")[
                            1] + '.py').read().replace('\n', '')  # pipe stdout to variable
                for key in module.properties:
                    if str(module.properties[key]).__contains__(signalWord):
                        module.properties[key] = os.popen(
                            'python3 ' + module.properties[key].split("/")[1] + '.py').read().replace('\n',
                                                                                                                 '')

            for interface in vm.interfaces:
                if str(interface.privateIP).__contains__(signalWord):
                    interface.privateIP = os.popen(
                        'python3 ' + interface.privateIP.split("/")[1] + '.py').read().replace('\n', '')
                if str(interface.subnetID).__contains__(signalWord):
                    interface.subnetID = os.popen(
                        'python3 ' + interface.subnetID.split("/")[1] + '.py').read().replace('\n', '')
                if str(interface.allocationType).__contains__(signalWord):
                    interface.allocationType = os.popen(
                        'python3 ' + interface.allocationType.split("/")[1] + '.py').read().replace('\n', '')

        for route in subnet.routes:
            if str(route.nextHopIp).__contains__(signalWord):
                route.nextHopIp = os.popen(
                    'python3 ' + route.nextHopIp.split("/")[1] + '.py').read().replace('\n', '')
            if str(route.nextHopType).__contains__(signalWord):
                route.nextHopType = os.popen(
                    'python3 ' + route.nextHopType.split("/")[1] + '.py').read().replace('\n', '')
            if str(route.routePrefix).__contains__(signalWord):
                route.routePrefix = os.popen(
                    'python3 ' + route.routePrefix.split("/")[1] + '.py').read().replace('\n', '')
    os.chdir('../src')

def readSubnets(mountTemplate, idOffset):
    '''
    Parses the subnets from a template and returns the subnets objects
    :param mountTemplate: template to parse for subnets
    :param idOffset: offset that is multiplied to the subnet IDs from the parsed subnets
    :return: a list of subnet objects
    '''

    subnetObjects = []
    with open("../templates/" + mountTemplate, "r+") as stream:
        data = yaml.load(stream)
        for subnet in data:
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
                        interfacesObjects.append(Interface(interface[0] + idOffset, interface[1], interface[2]))
                    vmObj.interfaces = interfacesObjects

                    Network.numberOfVms += 1
                    subnetVms.append(vmObj)
            subnetObjects.append(Subnet(Network.numberOfSubnets, subnetPrefix, vms=subnetVms, routes=routesObj,
                                        mountTemplate=mountTemplate))
            Network.numberOfSubnets += 1
        return subnetObjects


def readVM(mountTemplate):
    '''
    Parses a VM from a vm template and returns the parsed data in a vm object.
    :param mountTemplate: template that contains the VM
    :return: vm object containing parsed data from template
    '''

    vmObjects = []
    with open("templates/" + mountTemplate, "r+") as stream:
        data = yaml.load(stream)
        for vm in data:
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
                        moduleObj.mountTemplate = module['mountTemplate']
                    except (KeyError, TypeError):
                        moduleObj.mountTemplate = None

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
                vmObjects.append(vmObj)
    return vmObjects
