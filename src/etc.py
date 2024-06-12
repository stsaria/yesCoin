import json

usersFile = 'data/users.json'
nodesFile = 'data/nodes.json'
chainFile = 'data/chain.json'

def saveData(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def loadData(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

users = loadData(usersFile)