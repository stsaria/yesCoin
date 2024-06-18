from flask import Flask, request, jsonify
from etc import *

app = Flask(__name__)

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
    syncChain = request.json
    print(syncChain)