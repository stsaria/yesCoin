from flask import Flask, request, jsonify
from etc import *
from blockchain import BlockChain
import requests

app = Flask(__name__)
chain = []

blockchain = BlockChain()

@app.route("/", methods=["GET"])
def getNodes():
    return jsonify({"hello": "world"}), 200

@app.route("/nodes", methods=["GET"])
def getNodes():
    return jsonify(loadData(nodesFile)), 200

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