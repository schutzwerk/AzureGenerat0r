# Introduction / Blog Post <br />

* For a first introudction to AzureGenerat0r please refer to the corresponding [blog post](https://www.schutzwerk.com/en/43/posts/azuregenerat0r/ ).

# What is AzureGenerat0r? <br />
AzureGenerat0r is a framework that creates infrastructure (VMs, NICs, subnets, routes,..) in Microsoft Azure via Terraform and uses ansible playbooks to configure virtual machines.
Playbooks can be used to specify properties of a virtual machine like
* running services
* vulnerabilities
* installed software
* OS/application configurations

The infrastructure and playbooks can be defined in a specification.
AzureGenerat0r is useful for setting up environments for test and training purposes.
# Installing and Running <br />
* Requirements: python >= 3.4, pipenv, terraform 0.13.x
* Run `pipenv install --python 3` to install the virtual environment and login using `pipenv shell`.
* Run `python3 AzureGenerat0r.py --setup` to setup AzureGenerat0r.
* Create a resource group in Azure and put the name and location in the file `configuration.yml`.
* Follow this guide, to configure Terraform for Azure. (https://docs.microsoft.com/en-us/azure/virtual-machines/linux/terraform-install-configure#set-up-terraform-access-to-azure)
  This guide describes how to create an AD Service Principal and an App. Make sure both are allowed to create and delete resources in the specific resource group and subscription you want to use. <br />
  Put the keys and IDs to `configuration.yml`.
* Specify user credentials for the VMs and ssh keys in `configuration.yml`. Consider Azure's credential requirements. (https://docs.microsoft.com/de-de/azure/virtual-machines/windows/faq#what-are-the-password-requirements-when-creating-a-vm)
* Specify your network in `specification.yml`.
* Run `python3 AzureGenerat0r.py` to start AzureGenerat0r.
* After usage, logout from the virtual environment via `exit`.

# Usage <br />
Specify the network in `specification.yml`. Then start AzureGenerat0r: <br />
`create`  - creates infrastructure in Azure. <br />
`enrich`  - deploys playbooks to existing VMs<br />
`godmode` - creates infrastructure and enriches machines<br />
`destroy` - destroys infrastructure in Azure (runs `terraform destroy -auto-approve`)<br />
`refresh` - refreshes Terraform state file (a refresh is required if any changes are made manually by the Azure Portal) <br />
`ips` - shows private and public IP addresses of existing virtual machines<br >
`exit`    - exit AzureGenerat0r<br />

Example: <br>
Let's create the network specified in `specifications/ad_testlab.yml`. Create it using the `create` command.
<br>
![Alt text](/.repoResources/demo/createResources.gif?raw=true "Create Resources in Azure") <br/>
After creating the infrastructure, AzureGenerat0r returns the public and private ip addresses of the VMs. <br />
You can use rdp to access the Windows VMs with the credentials specified in `configuration.yml`.
Since no trust chain is established for the certificates used for the rdp connection, the `rdesktop` client will fail with an error.
I recommend using `remmina` or `xfreerdp` for the connection. For example:`xfreerdp /u:"<username>" /v:<IP>:3389`. <br/>
SSH access to linux VMs is secured by public-key authentication using the keys specified in `configuration.yml`. <br/>
If you don't configure NSG or similar, all VMs are reachable for anybody over the internet. <br/>
Now use `enrich` to apply the playbooks to the VMs. This is done multithreaded. The output
of each thread is piped to `output<VMNumber><PlaybookNumber>.txt` in the `ansible` directory. So you can observe
each ansible deployment. <br>
![Alt text](/.repoResources/demo/enrichVMs.gif?raw=true "Use playbooks to configure VMs") <br>
Don't forget to destroy the infrastructure. Please check out the best practices!
# Features <br />
* Specify playbooks for linux and windows virtual machines.
* Specify parameters for playbooks.
* Let AzureGenerat0r choose random playbooks. Can be used to create random vulnerable VMs.
* Filter playbooks based on properties such as CVE.
* Use plugins to generate values for the specification. Can be used to generate IDs, names, passwords etc.
* Deploy playbooks in two stages for handling time based dependencies. Enables delayed deployment of playbooks.
* Easily adjust default values for attributes of resources in the top of Controller.py.<br />

# Use Case: Active Directory Multi Tier Environment<br />
There are already various playbooks for the deployment of an Active Directory. The currently developed playbooks are capable of <br />
* creating a domain
* promoting a computer to a domain controller
* adding users and computers to a domain
* randomly creating multiple user accounts and their passwords (powered by [Youzer](https://stealingthe.network/rapidly-creating-fake-users-in-your-lab-ad-using-youzer/))
* organizing users in groups and computers in organizational units
* importing GPOs <br />

Combining these playbooks, a number of options are available to configure Active Directory as needed. Especially
the ability to import GPOs is very powerful,
as GPOs itself can be used to create complex Active Directories like an Active Directory Tier Model.
The specification in `specifications/ad_testlab.yml` creates an Active Directory containing one domain controller, and two domain computers.
Furthermore it realizes Tier Model where users and computers are separated into (in our case two) logical tiers. Tier0 contains the domain controller,
where only the Active Directory Administrator (ADA) has access to. Tier1 represents a sales department using two domain computers, where 200 employees and one admin
have access to.
As it takes its time to configure a Tier Model from scratch, if you
need a tier separated AD lab for training or test purposes, you can
use this specification. <br /> These are the precautions required for
using the `import_gpo` playbook with your own GPO: <br />

* Setup an AD.
* Create and deploy the GPO manually.
* Backup the GPO and try to import it into a new AD.
* If required, create a migration table to resolve unresolved references.
* Copy the GPO and the migration table into the `import_gpo` playbook.
* Adjust the parameters of the playbook.
* Restart the affected computers. The `add_computer_to_ad` playbook restarts computers after adding them to the AD.
So it is recommended to import the GPOs first and add the computers using this playbook afterwards.

# Best practices <br />
- If you do not want to spent all your money on Azure, don't forget to destroy or shutdown the created resources. A logout script running `terraform destroy -auto-approve` in the `src` directory might be useful, to ensure your infrastructure gets destroyed, when shutting down your computer.
- Furthermore, I highly recommend using the Azure portal to check, if all resources have been destroyed successfully by the destroy command. In some cases it might be necessary to destroy the resources manually via the Azure Portal.
- In most cases, changes on an existing infrastructure (like adding or removing Subnets/VMs) will fail. If you want to make changes I recommend to destroy the existing infrastructure and deploy a new one. In contrast, you can deploy playbooks on existing VMs without any problems in most cases.