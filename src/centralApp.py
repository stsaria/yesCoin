from flask import Flask, request, jsonify

app = Flask(__name__)

nodes = []

@app.route('/register', methods=['POST'])
def registerNode():
    node = request.get_json()
    if node not in nodes:
        nodes.append(node)
    return jsonify(nodes), 201

@app.route('/nodes', methods=['GET'])
def getNodes():
    return jsonify(nodes), 200