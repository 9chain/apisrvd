import requests
import json
from .common import CustomError, make_data
import struct
from config import Config

def get_eth_transaction(bitcointransactionhash):
    headers = {"Content-type": "application/json"}

    # bitcointransactionhash = "0x" + "db70bdc1ad47843e3948bfc5263e6a2e3a5990c78e99bdfea50111e071391d61"
    bitcointransactionhash = "0x" + bitcointransactionhash
    data = {"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":[bitcointransactionhash],"id":1}
    resp = requests.post(Config.ETH_HOST, data=json.dumps(data), headers=headers, timeout=30)
    s = resp.content.decode()
    res = json.loads(s)
    error = res.get("error")
    if error:
        return None, error, s

    return res, None, res["result"]


def get_bitcoin_transaction(bitcointransactionhash):
    """
    {
      "block_hash": "000000000000000001edf3adf719dfc1263661d2c4b0ed779d004a2cbb7cca32",
      "block_height": 388463,
      "block_index": 1648,
      "hash": "469a96c847cf8bf1f325b6eec850f46488ed671930d62b54ed186a8031477a7d",
      "addresses": [
        "1K2SXgApmo9uZoyahvsbSanpVWbzZWVVMF"
      ],
      "total": 2940000,
      "fees": 10000,
      "size": 242,
      "preference": "low",
      "relayed_by": "104.130.119.148:8333",
      "confirmed": "2015-12-15T03:13:00Z",
      "received": "2015-12-15T03:00:03.182Z",
      "ver": 1,
      "double_spend": false,
      "vin_sz": 1,
      "vout_sz": 2,
      "data_protocol": "factom",
      "confirmations": 119432,
      "confidence": 1,
      "inputs": [
        {
          "prev_hash": "415aaf9f9daa65401bcc6c55a7101f8837441ec5417980f7c73de421b385d4b2",
          "output_index": 1,
          "script": "4730440220144f2884de0df5d39ddcbb27bf406c98fffce7da0ffda7b7f3d64a01ca62eb2d022008cd40c0193a007411721f702313233a3976f4c8f022e1e2c4e23bec7796db980121027e706cd1c919431b693a0247e4a239e632659a8723a621a91ec610c64f4173ac",
          "output_value": 2950000,c
          "sequence": 4294967295,
          "addresses": [
            "1K2SXgApmo9uZoyahvsbSanpVWbzZWVVMF"
          ],
          "script_type": "pay-to-pubkey-hash",
          "age": 388438
        }
      ],
      "outputs": [
        {
          "value": 0,
          "script": "6a284661000000003a984358041d6773351dd0a42a8d16778c6544b1196a03c6c41645340cd076a29b6b",
          "addresses": null,
          "script_type": "null-data",
          "data_hex": "4661000000003a984358041d6773351dd0a42a8d16778c6544b1196a03c6c41645340cd076a29b6b"
        },
        {
          "value": 2940000,
          "script": "76a914c5b7fd920dce5f61934e792c7e6fcc829aff533d88ac",
          "spent_by": "557382977a975b578bda203930aaba91c8e4922bae3d3070cee68973e4747ecc",
          "addresses": [
            "1K2SXgApmo9uZoyahvsbSanpVWbzZWVVMF"
          ],
          "script_type": "pay-to-pubkey-hash"
        }
      ]
    }

    {"error": "Transaction 469a96c847cf8bf1f325b6eec850f46488ed671930d62b54ed186a8031477a70 not found."}
    """
    btc_host = "https://api.blockcypher.com"
    # bitcointransactionhash = "469a96c847cf8bf1f325b6eec850f46488ed671930d62b54ed186a8031477a7d"
    # bitcointransactionhash = "469a96c847cf8bf1f325b6eec850f46488ed671930d62b54ed186a8031477a70"
    url = "{}/v1/btc/main/txs/{}".format(btc_host, bitcointransactionhash)
    resp = requests.get(url, timeout=30)
    s = resp.content.decode()
    res = json.loads(s)
    error = res.get("error")
    if error:
        return None, error

    return res, None

def make_op_return_datahex(dbheight, directoryblockkeymr):
    # dbheight, directoryblockkeymr = 15000, "4358041d6773351dd0a42a8d16778c6544b1196a03c6c41645340cd076a29b6b"
    a = struct.pack(">Q", dbheight)
    header = "Fa".encode()
    x = bytearray()
    x.extend(header)
    x.extend(a[2:])
    datahex = x.hex() + directoryblockkeymr
    return datahex

def make_eth_input(dbheight, directoryblockkeymr):
    datahex = make_op_return_datahex(dbheight, directoryblockkeymr)
    return "0x" + datahex
