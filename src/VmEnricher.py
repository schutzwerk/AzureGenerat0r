import re
import os
from src.Parser import *
import multiprocessing
import random
import yaml
import json

'''
contains all functions used to enrich virtual machines with software, vulnerabilities,...
'''

def createInventoryForWindows(ip, password, user):
    '''
    Creates an inventory for ansible.
    :param ip: ip of the target machine
    :param password: corresponding password
    :param user: user to access the machine
    :return: an ansible valid inventory containing credentials to access windows machines via WinRM
    '''
    host = "[windows]\n"
    ip = ip + "\n"
    variables = "[windows:vars]\n"
    ansibleUser = "ansible_user=" + user + "\n"
    ansiblePassword = "ansible_password=" + password + "\n"
    ansiblePort = "ansible_port=5986 \n"
    ansibleConnection = "ansible_connection=winrm \n"
    serverValidation = "ansible_winrm_server_cert_validation=ignore"
    inventory = host + ip + variables + ansibleUser + ansiblePassword + ansiblePort + ansibleConnection + serverValidation
    return inventory

def createInventoryForLinux(ip, user):
    '''
    Creates an inventory for ansible.
    :param ip: ip of the target machine
    :param user: user to access the machine
    :return: an ansible valid inventory containing credentials to access linux machines via ssh.
    '''

    host = "[linux]\n"
    ip = ip + "\n"
    variables = "[linux:vars]\n"
    ansibleUser = "ansible_user=" + user + "\n"
    return host + ip + variables + ansibleUser

def updateIPs():
    '''
    reads the public IPs from the ipListForAnsible.txt file using regex and writes them back to the model.
    These public IPs can be used by ansible to access the virtual machines.
    '''
    file = open('ipListForAnsible.txt', 'r')
    IPAdresses = []
    publicIPAdresses = []
    for line in file:
        IP = re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', line)
        if IP:
            IPAdresses.append(IP[0])
    # check if ip is private
    for IP in IPAdresses:
        IP = str(IP).replace(',', '')
        IP = re.findall(r'^(?!10\.0\..*).*', IP)
        if IP:
            publicIPAdresses.append(IP[0])

    VMs = Network.networkModel.getVMs()
    index = 0
    for IP in publicIPAdresses:
        VMs[index].publicIP = IP
        index += 1


def findFittingModule(vm, module):
    '''
    this method is getting called if no path for a module has been specified. This means the user want AzureGenerat0r to select a random module based on a type and/or properties.
    this method serches for a module fitting the specified requirements.
    :param vm: virtual machine for which the module will be applied.
    :param module: module object containing the constraints from the specification.
    :return: path to the module as string <OS>/<Type>/<Module> or None if no fitting module as been found.
    '''
    if vm.isLinux():
        # osStr because os is already in use (library)
        osStr = "linux"
    else:
        osStr = "windows"

    if module.hasType():
        moduleType = str(module.type)
    else:
        moduleType = random.choice(["software", "vulnerability", "config", "service"])

    resultModule = ""
    if module.hasProperties():
        # find fitting module
        fittingModules = []
        for moduleDir in os.listdir("../modules/" + osStr + "/" + moduleType):
            f = open("../modules/" + osStr + "/" + moduleType + "/" + moduleDir + "/metadata.yml")
            metadata = yaml.load(f.read())['properties']
            if all(item in metadata.items() for item in module.properties.items()):
                fittingModules.append(moduleDir)
        if fittingModules:
            resultModule = random.choice(fittingModules)
        else:
            return None
    else:
        # choose random module without properties
        resultModule = random.choice(os.listdir("../modules/" + osStr + "/" + moduleType))

    return osStr + "/" + moduleType + "/" + resultModule


def enrichMachine(vm, ip, jobID):
    '''
    applies a module to a virtual machine. check if a vm has to be accessed via ssh (for linux) or via winRM (for windows).

    :param vm: vm to apply the module
    :param ip: ip of the vm
    :param jobID: jobID used to keep track of multithreaded processes
    '''

    jobID = str(jobID)
    if vm.isLinux():
        # linux machine => grab public ssh keys
        os.system('bash getPublicKey.sh ' + ip + ' 2> /dev/null')
    # create hosts file for ansible command
    f = open('../ansibleMultithreading/hosts' + jobID, 'w+').close()
    f = open('../ansibleMultithreading/hosts' + jobID, 'w+')
    if vm.isLinux():
        f.write(createInventoryForLinux(ip, Configuration.user))
    else:
        f.write(createInventoryForWindows(ip, Configuration.password, Configuration.user))
    f.close()
    # run specified ansible playbook with commandLine arguments. Arguments passed as json.
    print('Begin Enrichement of machine: ' + ip)
    moduleNumber = 0
    for module in vm.modules:
        if module.hasPath():
            path = module.path
        else:

            path = findFittingModule(vm, module)
            print("randomized selection choosed " + str(path) + " for " + ip)
        if path:
            os.system(
                'ansible-playbook -i ../ansibleMultithreading/hosts' + jobID + ' ../modules/' + path + '/main.yml  1> ../ansibleMultithreading/output' + jobID + str(
                    moduleNumber) + '.txt --extra-vars \'' + json.dumps(module.args) + '\'')
        moduleNumber += 1
    print('Enrichment of machine ' + ip + ' completed')


def main():
    '''
    iterates the model searching for modules and starts the enrichment process for each module with a own thread.
    by reading the delayedEnrichment attribute it seperates the enrichment process into two stages. This can be
    used by users to overcome time based dependencies when enriching a machine.
    '''
    updateIPs()
    if not os.path.isdir('../ansibleMultithreading'):
        os.mkdir('../ansibleMultithreading')
    os.system('rm ../ansibleMultithreading/* 2> /dev/null')
    # stage 1 enrichment
    hostIndex = 0
    jobs = []
    VMs = Network.networkModel.getVMs()
    IPList = list(
        map(lambda x: x.publicIP, VMs))

    for VM in VMs:
        if VM.hasModule() & (VM.delayedEnrichment is False):
            process = multiprocessing.Process(target=enrichMachine, args=(VM, str(IPList[hostIndex]), hostIndex))
            jobs.append(process)
        hostIndex += 1
    for j in jobs:
        j.start()

    # Ensure all processes have finished
    for j in jobs:
        j.join()

    # stage 2 enrichment
    hostIndex = 0
    jobs = []
    for VM in VMs:
        if VM.hasModule() & (VM.delayedEnrichment is True):
            process = multiprocessing.Process(target=enrichMachine, args=(VM, IPList[hostIndex], hostIndex))
            jobs.append(process)
        hostIndex += 1
    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

    print('Enrichment completed')
