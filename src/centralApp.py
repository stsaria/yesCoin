from flask import Flask, request, jsonify
from etc import *

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def registerNode():
    global nodes
    node = request.get_json()
    if node not in nodes:
        nodes.append(node)
    saveData(nodesFile, nodes)
    return jsonify(nodes), 201

@app.route('/nodes', methods=['GET'])
def getNodes():
    return jsonify(loadData(nodesFile)), 200