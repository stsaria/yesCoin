import portalocker, json, time

usersFile = 'data/users.json'
nodesFile = 'data/nodes.json'
chainFile = 'data/chain.json'
blockchainFile = 'data/blockchain.json'

centralServers = [
    'http://192.168.1.39:11380'
]

def lockFile(file_path):
    with open(file_path, 'a') as f:
        try:
            # ファイルロックを取得
            portalocker.lock(f, portalocker.LOCK_EX)
            print(f'{file_path} is locked')
            time.sleep(3)  # 擬似的な処理時間のための待機
        finally:
            # ファイルロックを解放
            portalocker.unlock(f)
            print(f'{file_path} is unlocked')

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