import os

config = """subscriptionID:
tenantID:
appID:
clientSecret:
resourceGroup:
location:  # english name of the location, for example centralus.
sshKeyPrivateFile:
sshKeyPublicFile:
nameForLogging:
# password must fulfill Azure password requirements
user:
password:
# targeted azure version for terraform, do not change
terraformProviderVersion: =1.16.0
# configuration options for azure virtual machines
storageAccountType: Standard_LRS
vmSize: Standard_DS1_V2
vmOsVersion: latest
deleteOsDiskOnTermination: true
dataStorageAccountType: Standard_LRS """

spec = "# specify here. for example see specifications/repoExample"


def createConfigurationFile():
    with open('../configuration.yml', 'w+') as outfile:
        outfile.write(config)
        outfile.close()

def createSpecificationFile():
    with open('../specification.yml', 'w+') as outfile:
        outfile.write(spec)
        outfile.close()

'''
creates configuration and specification files
'''
def setup():
    createConfigurationFile()
    createSpecificationFile()