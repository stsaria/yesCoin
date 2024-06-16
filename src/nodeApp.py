import requests, datetime, hashlib, socket, jwt
from etc import *
from flask import Flask, request, make_response, redirect, url_for, session, render_template, jsonify
from functools import wraps
from blockchain import BlockChain

app = Flask(__name__)
app.secret_key = "3141592653589793238"

# 初期ノードリスト（公式ノード）
bootstrapNodes = [
    #{"ip": "127.0.0.1", "port": 11380}
]

# ノードを読み込み
nodes = loadData(nodesFile)

if not nodes:
    nodes = bootstrapNodes
    saveData(nodesFile, nodes)

blockchain = BlockChain()

def generateToken(username, password):
    # JWTトークン（ログイントークン）生成関数
    token = jwt.encode({
        "username": username,
        "password": password, 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.secret_key, algorithm="HS256")
    return token

def authenticate(username, password):
    # ユーザー認証関数
    if (hashlib.sha256(username.encode()).hexdigest()
    in users and users[hashlib.sha256(username.encode()).hexdigest()]["password"]
    == hashlib.sha256(password.encode()).hexdigest()):
        return True
    return False

@app.route("/login", methods=["GET", "POST"])
def login():
    # ログインエンドポイント
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if authenticate(username, password):
            token = generateToken(username, password)
            response = make_response(redirect(url_for("index")))
            # トークンをクッキーに保存
            response.set_cookie("token", token)
            return response
        else:
            return render_template("login.html", error="ログインに失敗しました")
    return render_template("login.html")


@app.route("/logout")
def logout():
    # ログアウトエンドポイント
    response = make_response(redirect(url_for("login")))
    # トークンを削除（ログアウト）
    response.delete_cookie("token")
    return response

@app.route("/register", methods=["GET", "POST"])
def register():
    # ユーザー登録エンドポイント
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if authenticate(username, password):
            return render_template("register.html", error="登録に失敗しました\n既に登録されています")
        
        # ユーザー名のハッシュ（アドレス）で保存
        address = hashlib.sha256(username.encode()).hexdigest()
        hashedPassword = hashlib.sha256(password.encode()).hexdigest()
        users[address] = {
            'password': hashedPassword,
            'balance': 0  # 初期残高を0に設定
        }
        saveData(usersFile, users)
        
        # indexに移動するために認証しておく
        if authenticate(username, password):
            response = make_response(redirect(url_for("index")))
            token = generateToken(username, password)
            response.set_cookie("token", token)
            return response
        return redirect(url_for("login"))
    return render_template("register.html")

def requiresAuth(f):
    # 認証が必要なエンドポイント用のデコレータ
    global session
    @wraps(f)
    def decorated(*args, **kwargs):
        # トークンを取得
        token = request.cookies.get("token")
        if not token:
            # トークンを持ってないのなら
            return redirect(url_for("login"))
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            if authenticate(data["username"], data["password"]):
                session["username"] = data["username"]
            else:
                session["username"] = None
                return redirect(url_for("login"))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.InvalidTokenError:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requiresAuth
def index():
    username = session['username']
    address = hashlib.sha256(username.encode()).hexdigest()
    balance = users[address]['balance']
    return render_template('index.html', username=username, address=address, balance=balance)

@app.route("/mine", methods=["GET"])
@requiresAuth
def mine():
    # マイニングエンドポイント
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock["proof"]
    proof = blockchain.proofOfWork(lastProof)
    address = hashlib.sha256(session["username"].encode()).hexdigest()
    blockchain.newTransaction(
        sender="0",
        recipient=address,
        amount=0.001,
    )

    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)

    return render_template("mine.html", block=block, balance=blockchain.getBalance(address))

@app.route("/send", methods=["GET", "POST"])
@requiresAuth
def send():
    # 送金
    if request.method == "POST":
        sender = hashlib.sha256(session["username"].encode()).hexdigest()
        recipient = request.form["recipient"]
        amount = float(request.form["amount"])
        if blockchain.getBalance(sender) < amount:
            return render_template("send.html", error="残高が不足しています")
        blockchain.newTransaction(sender, recipient, amount)
        return render_template("send.html", success="送金が成功しました")
    return render_template("send.html")

@app.route('/chain', methods=['GET'])
def fullChain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

def registerWithCentralServers():
    for centralServer in centralServers:
        try:
            response = requests.post(f"{centralServer}/register")
            if response.status_code == 201:
                print(f"中央サーバーノードを登録しました サーバー:{centralServer}")
        except requests.ConnectionError:
            print(f"中央サーバーに接続できませんでした サーバー:{centralServer}")

def getNodesFromCentralServers():
    nodes = []
    for centralServer in centralServers:
        try:
            response = requests.get(f"{centralServer}/nodes")
            if response.status_code == 200:
                newNodes = response.json()
                nodes.extend(newNodes)
        except requests.ConnectionError:
            print(f"中央サーバーに接続できませんでした サーバー:{centralServer}")
    return nodes

@app.route('/sync', methods=['GET'])
def syncBlockchain():
    global blockchain
    nodes = getNodesFromCentralServers()
    
    if not nodes:
        message = 'ノードが見つかりませんでした'
        return render_template('sync.html', message=message, nodes=nodes)
    
    longestChain = None
    maxLength = len(blockchain.chain)
    
    for node in nodes:
        try:
            response = requests.get(f"http://{node['ip']}:{node['port']}/chain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > maxLength and blockchain.validChain(chain):
                    maxLength = length
                    longestChain = chain
        except requests.ConnectionError:
            continue
    
    if longestChain:
        blockchain.chain = longestChain
        saveData(blockchainFile, blockchain.chain)
        message = 'ブロックチェーンが更新されました'
    else:
        message = '既存のブロックチェーンが最長です'
    
    return render_template('sync.html', message=message, nodes=nodes)
