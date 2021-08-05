import yaml

counter = -1

def main():
    global counter
    counter += 1
    return('domainmember-%s' % str(counter))