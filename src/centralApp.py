from flask import Flask, request, jsonify
from etc import *
from blockchain import BlockChain
import requests

app = Flask(__name__)
chain = []

blockchain = BlockChain()

@app.route("/", methods=["GET"])
def index():
    return jsonify({"hello": "world"}), 200

@app.route("/getCentralServers", methods=["GET"])
def getCentralServers():
    return jsonify({"centralServers": loadData(centralServers)}), 200

@app.route("/sync", methods=["POST"])
def sync():
    global blockchain, users
    syncData = request.json

    chain = syncData["chain"]
    length = len(chain)
    maxChainLength = len(blockchain.chain)
    if length > maxChainLength and blockchain.validChain(chain):
        blockchain.chain = chain
        saveData(chainFile, blockchain.chain)
    users = addUniqueKeys(users, syncData["users"])

    saveData(chainFile, chain)
    return jsonify({"chain": blockchain.chain, "users": users, "centralServers": centralServers}), 200

@app.route("/registerCentralServer", methods=["GET"])
def registerCentralServer():
    global centralServers
    try:
        response = requests.get(f"http://{request.remote_addr}:11380/")
        if response.status_code == 200 and "hello" in response.json():
            if response.json()["hello"] == "world":
                centralServers = addUniqueElements(centralServers, [f"http://{request.remote_addr}:11380"])
                saveData(centralServersFile, centralServers)
                return jsonify({"result": 0}), 200
        return jsonify({"result": 2}), 500
    except:
        return jsonify({"result": 1}), 500

def syncPeriodically():
    # 定期同期のための関数
    global centralServers
    while True:
        time.sleep(5)
        print("定期的な同期")
        connect = False
        for centralServer in centralServers:
            try:
                response = requests.get(f"{centralServer}/getCentralServers")
                centralServers = addUniqueElements(centralServers, response.json()["centralServers"])
                connect = True
            except requests.ConnectionError:
                print(f"エラー: 中央サーバーに接続できません\nサーバー:{centralServer}")
                centralServers.remove(centralServer)
            except Exception as e:
                message += f"エラー: {e} サーバー:{centralServer}<br/>\n"
                if not isValidUrl(centralServer): centralServers.remove(centralServer)
        saveData(centralServersFile, centralServers)
        if not connect:
            print("エラー: どの中央サーバーにも接続できませんでした。\ndata/centralServers.jsonを削除し、初期ノードを設定してください")
        time.sleep(30)

def reigsterSelfCentralServer():
    global centralServers
    connect = False
    for centralServer in centralServers:
        try:
            response = requests.get(f"{centralServer}/registerCentralServer")
            result = response.json()["result"]
            if result == 0:
                connect = True
                print(f"登録: サーバー: {centralServer}")
            elif result == 1:
                print(f"エラー: 不明\nサーバー: {centralServer}")
            elif result == 2:
                print(f"エラー: このサーバーは相手のサーバーと合いません\nサーバー: {centralServer}")
        except requests.ConnectionError:
            print(f"エラー: 中央サーバーに接続できません\nサーバー: {centralServer}")
            centralServers.remove(centralServer)
        saveData(centralServersFile, centralServers)
    if not connect:
        print("エラー: どの中央サーバーにも接続できませんでした。\ndata/centralServers.jsonを削除し、初期ノードを設定してください")