from web3 import Web3
import web3  # 注意需要单独 import 模块才能拿版本
import base58
import ecdsa
import hashlib

print("✅ Web3 版本:", web3.__version__)
print("✅ Base58 示例:", base58.b58encode(b'hello').decode())