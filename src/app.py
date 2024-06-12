import requests
from etc import *
from flask import Flask, jsonify, request, make_response, redirect, url_for, session, render_template
from flask_bcrypt import generate_password_hash, check_password_hash
from functools import wraps
from blockchain import BlockChain
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # セッションを使用するための秘密鍵

# 初期ノードリスト（公式ノード）
bootstrapNodes = [
    {"ip": "127.0.0.1", "port": 5001},
    {"ip": "127.0.0.1", "port": 5002},
]


nodes = loadData(nodesFile)

if not nodes:
    nodes = bootstrapNodes
    saveData(nodesFile, nodes)

blockchain = BlockChain()

# ユーザー認証
def authenticate(username, password):
    if username in users and check_password_hash(users[username], password):
        return True
    return False

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='ログインに失敗しました')
    return render_template('login.html')

# ログアウト
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ユーザー登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashedPassword = generate_password_hash(password).decode('utf-8')
        users[username] = hashedPassword
        saveData(usersFile, users)
        return redirect(url_for('login'))
    return render_template('register.html')

# ユーザー認証のデコレータ
def requiresAuth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# インデックスページ
@app.route('/')
@requiresAuth
def index():
    return render_template('index.html', username=session['username'])

# ノード一覧を表示するエンドポイント
@app.route('/nodes', methods=['GET'])
def getNodes():
    return render_template('nodes.html', nodes=nodes)

# ノード登録エンドポイント
@app.route('/nodes/register', methods=['POST'])
def registerNode():
    newNode = request.get_json()
    nodes.append(newNode)
    saveData(nodesFile, nodes)
    return redirect(url_for('getNodes'))

# ノードに接続するエンドポイント
@app.route('/nodes/connect', methods=['GET'])
def connectNodes():
    for node in nodes:
        print(f"Connecting to node {node['ip']}:{node['port']}")
    return render_template('connectNodes.html', nodes=nodes)

# ブロックチェーン同期エンドポイント
@app.route('/sync', methods=['GET'])
def syncBlockchain():
    global blockchain
    longestChain = None
    maxLength = len(blockchain.chain)
    
    for node in nodes:
        response = requests.get(f"http://{node['ip']}:{node['port']}/chain")
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            
            if length > maxLength and blockchain.validChain(chain):
                maxLength = length
                longestChain = chain
    
    if longestChain:
        blockchain.chain = longestChain
        saveData(chainFile, blockchain.chain)
        message = 'ブロックチェーンが更新されました'
    else:
        message = '既存のブロックチェーンが最長です'
    
    return render_template('sync.html', message=message)

# マイニングエンドポイント
@app.route('/mine', methods=['GET'])
@requiresAuth
def mine():
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)

    blockchain.newTransaction(
        sender="0",
        recipient=session['username'],
        amount=1,
    )

    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)

    return render_template('mine.html', block=block)