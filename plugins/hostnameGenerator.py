import yaml

if __name__ == '__main__':
    with open("hostnameGenerator.storage.yml", "r+") as storageFile:
        data = yaml.load(storageFile)
        counter = int(data['idCounter'])
        counter += 1
        storageFile.seek(0)
        storageFile.truncate()
        yaml.dump(dict(idCounter = counter), storageFile, default_flow_style=False)
        storageFile.close()
        print('domainMember-' + str(counter))

def init():
    storage = dict(idCounter = -1)
    with open('hostnameGenerator.storage.yml', 'w') as storageFile:
        yaml.dump(storage, storageFile, default_flow_style=False)
        storageFile.close()