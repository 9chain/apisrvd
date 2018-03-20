from flask import Flask, request
from hexlib import unhex
import functools

import json
import time
import traceback
import wtcrecord

from jsonres import *
from factom import *
from config import Config


app = Flask(__name__)


ApiKeyMap = {
    "test": "apikey"
}
#
# def invalid_request(id):
#     CODE = -32600
#     MESSAGE = "Invalid Request"
#     return json.dumps({"jsonrpc": "2.0", "id": id or 0, "error": {"message": MESSAGE, "code": CODE}})


dispatcher = dict()
@app.route('/v1', methods=["POST","GET"])
def application():
    headers = request.headers
    username, apikey = headers.get("X-Username"), headers.get("X-Api-Key")
    if not (username and apikey and ApiKeyMap.get(username) == apikey):
        err = {"jsonrpc": "2.0", "id": 0, "error": {"message": "invalid username/apikey", "code": -32601}}
        return json.dumps(err)

    method, jsonrpc, id, params = None, None, 0, None
    try:
        r = json.loads(request.data.decode())
        method, jsonrpc, id, params = r.get("method"), r.get("jsonrpc"), r.get("id"), r.get("params")
        if not id:
            return invalid_request_error(0)

        if not (method and jsonrpc and params):
            return invalid_request_error(id)

        func = dispatcher.get(method)
        if not func:
            return method_not_found_error()

        result = func(params)
        return json.dumps({"jsonrpc": "2.0", "id": id, "result": result})
    except (TypeError, ValueError):
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": {"code": -32700, "message": "Parse error"}})
    except CustomError as e:
        print("custom",  e.error)
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": e.error})
    except CustomError2 as e:
        err = e.error
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": err})
    except Exception as e :
        traceback.print_exc()
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": {"code": -32603, "message": "Internal error"}})


def addmethod(method):
    def inner_dec(f):
        dispatcher[method] = f
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(args, kwargs)

        return wrapped
    return inner_dec


@addmethod("create-entry")
def commit_entry_wtc(params):
    """
    创建entry
    params = {
        "chainid": chainid, # str
        "extids": extids,   # [str, ...]
        "content": content, # dict
        "ecpub": ecpub      # str, ec address
    }
    e.g.
    content = {
        "desc": "created at: 2018-02-07 06:48:47",
        "timestamp": 1517986127,
        "ext": 3775268,
        "city": "Ghuangzhou"
    }
    """

    content = params.get("content")
    if not content:
        return invalid_param_error()

    extids, chainid, content = [], Config.CHAINID, content
    ecpub = params.get("ecpub", Config.ECPUB)

    # compose entry
    res, error = get_compose_entry(ecpub, chainid, extids, content)
    if error:
        return factom_error(error)

    commit, reveal = res["commit"], res["reveal"]

    # commit entry
    commit_res, error = commit_entry(commit["params"]["message"])
    if error:
        if error["code"] == -32011:  # Repeated Commit
            entryhash, txid = error["entryhash"], error["txid"]
            return {"entryhash": entryhash, "message": "Repeated Committed"}
        return factom_error(error)

    time.sleep(0.1)

    # reveal entry
    reveal_res, error = reveal_entry(reveal["params"]["entry"])
    # {'message': 'Entry Reveal Success', 'entryhash': '7c0401ef348aa8820babdc0c95e5a58ce4917a5b56da55a38fe7dd6a7ededb68', 'chainid': '46ba158332765c40c88f258b1b8650379b0b50f402f4504197eb6e313a5ec235'}
    if error:
        return factom_error(error)

    entryhash = reveal_res["entryhash"]
    return {"entryhash": entryhash}


@addmethod("entry")
def entry_wtc(params):
    """
    检索一个entryhash对应的内容
    params = {"entryhash": entryhash}
    """
    entryhash = params.get("entryhash")
    if not entryhash:
        return invalid_param_error()

    entry_res, error = get_entry(entryhash)
    if error:
        return factom_error(error)
    extids, chainid, content = entry_res["extids"], entry_res["chainid"], entry_res["content"]
    return {"content": unhex(content)}

@addmethod("status")
def status_wtc(params):
    """
    检索一个entryhash对应的内容
    params = {"entryhash": entryhash}
    """
    entryhash = params.get("entryhash")
    if not entryhash:
        return invalid_param_error()

    entry_res, error = get_entry_status(entryhash)
    if error:
        return factom_error(error)
    return entry_res



@addmethod("receipt")
def receipt_wtc(params):
    """
    到btc检验entryhash是否为真
    params = {"entryhash": entryhash}
    """
    entryhash = params.get("entryhash")
    if not entryhash:
        return invalid_param_error()

    # 在factom查询receipt
    res, error = get_receipt(entryhash)
    if error:
        return factom_error(error)

    receipt_res = res["receipt"]

    transactionhash = receipt_res.get("bitcointransactionhash")
    if transactionhash:
        receipt_res["ethtransactionhash"] = transactionhash
        del receipt_res["bitcointransactionhash"]
    blockhash = receipt_res.get("bitcoinblockhash")
    if blockhash:
        receipt_res["ethblockhash"] = blockhash
        del receipt_res["bitcoinblockhash"]
    return {"receipt": receipt_res}


@addmethod("validate")
def validate_entry_wtc(params):
    """
    到btc检验entryhash是否为真
    params = {"entryhash": entryhash}
    """
    entryhash = params.get("entryhash")
    if not entryhash:
        return invalid_param_error()

    # 在factom查询receipt
    res, error = get_receipt(entryhash)
    if error:
        return factom_error(error)

    # 在factom校验receipt
    receipt_res = res["receipt"]
     # _, error = validate_receipt(json.dumps(receipt_res))
     # if error:
     #     return factom_error(error)

     # 检查factom是否anchor到btc上了
    bitcointransactionhash, bitcoinblockhash = receipt_res.get("bitcointransactionhash"), receipt_res.get("bitcoinblockhash")
    if not (bitcoinblockhash and bitcointransactionhash):
        return receipt_error("missing blockhash/transactionhash!")

    # 去btc获取transaction的记录
    eth_res, error, eth_result = get_eth_transaction(bitcointransactionhash)    # TODO
    if error:
        return receipt_error(error)

    # def get_data_hex(outputs):
    #     for output in outputs:
    #         data = output.get("data_hex")
    #         if data:
    #             return data
    #     else:
    #         raise CustomError("missing data_hex")

    # 获取 op_return的内容： data_hex
    datahex = eth_res["result"]["input"]
    datahex = datahex
    entryblockkeymr = receipt_res["entryblockkeymr"]
    directoryblockkeymr = receipt_res["directoryblockkeymr"]
    #print("datahex:{} directoryblockkeymr:{}".format(datahex, directoryblockkeymr))

    # 获取dbheight
    entryblock, error = get_entry_block(entryblockkeymr)
    if error:
        return blockchain_error("missing entryblockkeymr:" + entryblockkeymr)

    # 校验data_hex
    dbheight = entryblock["header"]["dbheight"]
    #print("dbheight:{}".format(dbheight))
    op_return = make_eth_input(dbheight, directoryblockkeymr)
    #print("datahex:{} op_return:{}".format(datahex, op_return))
    if datahex != op_return:
        return blockchain_error("missmatch data_hex in btc")

    return {"message": "success", "ethereum_tx_info": eth_result, "directoryblockkeymr": directoryblockkeymr}



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)
