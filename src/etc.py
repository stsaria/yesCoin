import portalocker, json, time

usersFile = 'data/users.json'
nodesFile = 'data/nodes.json'
chainFile = 'data/chain.json'
blockchainFile = 'data/blockchain.json'

centralServers = [
    'http://192.168.1.39:11380'
]

def saveData(filename, data):
    try:
        with open(filename, 'w') as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            json.dump(data, f)
            time.sleep(2)
            portalocker.unlock(f)
    except:
        pass

def loadData(filename, empty=[]):
    try:
        with open(filename, 'r') as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            data = json.load(f)
            time.sleep(2)
            portalocker.unlock(f)
    except:
        data = empty
    return data

users = loadData(usersFile, empty={})
nodes = loadData(nodesFile)