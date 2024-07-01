import portalocker, json, time, os, re

usersFile = "data/users.json"
chainFile = "data/chain.json"
centralServersFile = "data/centralServers.json"
secretKeyFile = "data/secretKey.json"

def saveData(filename, data):
    try:
        with open(filename, "w") as f:
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
        with open(filename, "r") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            data = json.load(f)
            time.sleep(2)
            portalocker.unlock(f)
    except:
        data = empty
    return data

def addUniqueElements(a1, a2, url=False):
    result = a1
    for i in a2:
        if url and i[-1] == "/": i = i.rstrip("/")
        if not i in result:
            result.append(i)
    return result

def addUniqueKeys(d1 : dict, d2 : dict):
    # 辞書の足し算
    result = dict(d1)
    for key, value in d2.items():
        if not key in result:
            result[key] = value
    return result

def isValidUrl(url):
    # URLの正規表現パターン
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// または https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # ドメイン名
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IPv4アドレス
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # IPv6アドレス
        r"(?::\d+)?"  # オプションのポート番号
        r"(?:/?|[/?]\S+)$", re.IGNORECASE)
    return re.match(regex, url) is not None

users = loadData(usersFile, empty={})
centralServers = loadData(centralServersFile)
if os.path.isfile("BOOTSTRAPSERVER"):
    with open("BOOTSTRAPSERVER") as f:
        if isValidUrl(f.read()):
            centralServers.append(f.read())
if centralServers == []:
    try:
        centralServers.append(input("初期中央サーバー(例: http://xxx.com:11380): "))
        with open("BOOTSTRAPSERVER", mode="w") as f:
            f.write(centralServers[0])
        saveData(centralServersFile, centralServers)
    except EOFError:
        # Systemdとかで実行したときに落ちないように
        pass