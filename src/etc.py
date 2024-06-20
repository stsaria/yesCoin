import portalocker, json, time

usersFile = 'data/users.json'
chainFile = 'data/chain.json'
centralServersFile = 'data/centralServers.json'

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
    # 初期化？
    if "data" in locals(): del data
    try:
        with open(filename, 'r') as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            data = json.load(f)
            time.sleep(2)
            portalocker.unlock(f)
    except:
        data = empty
    return data

def addUniqueElements(a1, a2):
    result = list(set(a1).union(set(a2)))
    return result

def addUniqueKeys(d1 : dict, d2 : dict):
    # 辞書の足し算
    result = dict(d1)
    for key, value in d2.items():
        if not key in result:
            result[key] = value
    return result

users = loadData(usersFile, empty={})
centralServers = loadData(centralServersFile)
if centralServers == []:
    centralServers.append(input("初期中央サーバー(例: http://xxx.com:11380): "))
    saveData(centralServersFile, centralServers)