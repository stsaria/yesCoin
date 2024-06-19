from flask import Flask, request, jsonify
from etc import *
from blockchain import BlockChain

app = Flask(__name__)
chain = []

blockchain = BlockChain()

@app.route("/register", methods=["GET"])
def registerNode():
    global nodes
    node = {"ip": request.remote_addr, "port": 11380}
    if node not in nodes:
        nodes.append(node)
    saveData(nodesFile, nodes)
    return jsonify(nodes), 201

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
    return jsonify({"result": 0, "chain": blockchain.chain, "users": users}), 200