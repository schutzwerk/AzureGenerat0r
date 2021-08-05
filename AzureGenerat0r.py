#!/usr/bin/env python
#
import sys, os, readline, json, argparse, paramiko
from src.Model import *
from src.Controller import *
from src.Completer import Completer
from src.Setup import setup

def print_banner():
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


def print_usage():
    '''
    prints the usage of AzureGenerat0r
    '''

    print(
        "Commands \n"
        "create      - creates infrastructure in azure \n"
        "enrich      - enriches existing VMs in Azure \n"
        "godmode     - creates infrastructure and enriches machines in one (long-lasting) step. \n"
        "destroy     - destroys infrastructure in Azure \n"
        "ips         - shows IPs of existing VMs \n"
        "refresh     - refreshes Terraform state file \n"
        "exit        - exit AzureGenerat0r \n \n")
        

def read_commands():
    '''
    a loop where commands are read and executed
    '''

    completer = Completer(
        ["create", "destroy", "enrich", "exit", "godmode", "help", "refresh", "ips"])
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    exit = False
    try:
        while exit is False:
            command = input(">> ")
            if command == "create":
                Specification.init()    
                Mapper.process(Specification.data)
                Pluginer.process(Specification.data)
                Connecter.process(Specification.data)
                Predeployer.process(Specification.data)
                Deployer.process(Specification.data)
            elif command == "enrich":
                Specification.init()
                Pluginer.process(Specification.data_enricher) 
                Enricher.process(Specification.data_enricher)
            elif command == "godmode":
                Specification.init()    
                Mapper.process(Specification.data)
                Pluginer.process(Specification.data)
                Connecter.process(Specification.data)
                Predeployer.process(Specification.data)
                Deployer.process(Specification.data)
                Pluginer.process(Specification.data_enricher)
                Enricher.process(Specification.data_enricher)
            elif command == "ips":
                os.system("terraform output")
            elif command == "destroy":
                os.system("terraform destroy --auto-approve")
            elif command == "refresh":
                os.system("terraform refresh")
            elif command == "help":
                print_usage()
            elif command == "exit":
                sys.exit(0)
    except (KeyboardInterrupt):
        pass

if __name__ == '__main__':
    # setup
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', action='store_true')
    args = parser.parse_args()
    if args.setup:
        setup()
        exit(0)

    os.chdir('./src')
    Configuration.init()
    # set environment for ansible 
    os.environ['ANSIBLE_HOST_KEY_CHECKING'] = str(Configuration.ansible_host_key_checking)
    
    print_banner()
    print_usage()
    read_commands()
