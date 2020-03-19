#!/usr/bin/env python
#
import sys, os, readline
from src import Preprocessor, VmCreator, VmEnricher, Parser
from src.Model import Network, Configuration
import json
from src.Completer import Completer
from src.Setup import setup
import argparse


def printBanner():
    '''
    prints the banner of AzureGenerat0r
    '''

    print("""
      
  ___                     _____                           _   _____      
 / _ \                   |  __ \                         | | |  _  |     
/ /_\ \_____   _ _ __ ___| |  \/ ___ _ __   ___ _ __ __ _| |_| |/' |_ __ 
|  _  |_  / | | | '__/ _ \ | __ / _ \ '_ \ / _ \ '__/ _` | __|  /| | '__|
| | | |/ /| |_| | | |  __/ |_\ \  __/ | | |  __/ | | (_| | |_\ |_/ / |   
\_| |_/___|\__,_|_|  \___|\____/\___|_| |_|\___|_|  \__,_|\__|\___/|_|   
                                                                         
                                                                         """)


def printUsage():
    '''
    prints the usage of AzureGenerat0r
    '''

    print(
        "Commands \n"
        "create      - creates infrastructure in azure \n"
        "enrich      - enriches existing VMs in Azure \n"
        "godmode     - creates infrastructure and enriches machines in one (long-lasting) step. \n"
        "destroy     - destroys infrastructure in Azure \n"
        "showIPs     - shows IPs of existing VMs \n"
        "reload      - reinitializes the model by reading the specification \n"
        "printModel  - prints current model \n"
        "refresh     - refreshes Terraform state file \n"
        "exit        - exit AzureGenerat0r \n \n")



def initializeModel():
    '''
    initializes the model by using the Parser and the Preprocessor
    '''

    Network.networkModel = None
    Network.numberOfSubnets = 0
    Network.numberOfVms = 0
    Network.subnetDefaultId = 1
    Parser.parseSpecification()
    Preprocessor.processTemplates()
    Preprocessor.processPlugins()


def readCommands():
    '''
    a loop where commands are read and executed
    '''

    completer = Completer(
        ["create", "destroy", "enrich", "exit", "godmode", "help", "printModel", "refresh", "reload", "showIPs"])
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    exit = False
    try:
        while exit is False:
            command = input(">> ")
            if command == "create":
                VmCreator.main()
            elif command == "enrich":
                VmEnricher.main()
            elif command == "godmode":
                VmCreator.main()
                VmEnricher.main()
            elif command == "showIPs":
                os.system("terraform output")
            elif command == "reload":
                initializeModel()
                print("The specification has been reloaded successfully.")
            elif command == "destroy":
                os.system("terraform destroy --auto-approve")
            elif command == "refresh":
                os.system("terraform refresh")
            elif command == "printModel":
                print(repr(Network.networkModel))
            elif command == "help":
                printUsage()
            elif command == "exit":
                sys.exit(0)
    except (KeyboardInterrupt):
        pass


if __name__ == '__main__':
    os.chdir("./src")
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', action='store_true')
    args = parser.parse_args()
    if args.setup:
        setup()
        exit(0)
    Parser.parseConfiguration()
    os.system('ssh-add ' + Configuration.sshKeyPrivate)  # add priv. key for ansible
    printBanner()
    printUsage()
    initializeModel()
    readCommands()
