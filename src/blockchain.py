import datetime, hashlib, json
from etc import *

class BlockChain:
    def __init__(self, miningDifficulty = 7):
        # チェーンデータの読み込み
        self.chain = loadData(chainFile)
        self.transactions = []
        self.difficulty = miningDifficulty # 難易度を設定
        if not self.chain:
            self.newBlock(100, previousHash='1')
    def newBlock(self, proof, previousHash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'transactions': self.transactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1]),
        }

        # 現在のトランザクションリストをリセット（ファイルに保存）
        self.transactions = [] 
        self.chain.append(block)
        # チェーンデータを保存
        saveData(chainFile, self.chain)
        return block
    
    def newTransaction(self, sender, recipient, amount):
        # 新しいトランザクションを作成してトランザクションリストに追加
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.lastBlock['index'] + 1
    
    @staticmethod
    def hash(block):
        # ブロックのハッシュ値を計算する
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()
    
    @property
    def lastBlock(self):
        # 最後のブロックを返す
        return self.chain[-1]

    def proofOfWork(self, lastProof):
        # ブロックチェーンの新しいブロックを生成するための証明
        proof = 0
        while not self.validProof(lastProof, proof):
            proof += 1
        return proof

    def validProof(self, lastProof, proof):
        # ハッシュが正しいか判別
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:self.difficulty] == "0" * self.difficulty
    
    def getBalance(self, address):
        # 所持金表示
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        return balance
    
    @classmethod
    def validChain(cls, chain):
        for i in range(1, len(chain)):
            if chain[i]['previousHash'] != cls.hash(chain[i - 1]):
                return False
        return True