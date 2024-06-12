import datetime, hashlib, json
from etc import *
from time import time
from urllib.parse import urlparse

class BlockChain:
    def __init__(self):
        self.chain = loadData(chainFile)
        self.transactions = []
        # チェーンが空ならジェネシスブロックを作成
        if not self.chain:
            self.newBlock(previousHash='1', proof=100)

    def newBlock(self, proof, previousHash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'transactions': self.transactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1]),
        }
        self.transactions = []
        self.chain.append(block)
        saveData(chainFile, self.chain)
        return block

    def newTransaction(self, sender, recipient, amount):
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.lastBlock['index'] + 1

    @property
    def lastBlock(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    def proofOfWork(self, lastProof):
        proof = 0
        while self.validProof(lastProof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validProof(lastProof, proof):
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == "0000"