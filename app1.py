from flask import Flask, request
from hexlib import unhex

import json
import time
import traceback
import wtcrecord

from factom import *
from jsonres import *
from config import Config

import factom
app = Flask(__name__)


@app.route('/v1/nametoid', methods=["POST"])
def nametoid():
    """
    把extids转换成chainid
    params = {"extids": extids}
    extids = ["x", ...]
    """
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        extids = params["extids"]
        chainid = factom.nametoid(extids)
        return json_result({"chainid":chainid})
    except AttributeError as e:
        return internal_error(e.args[0])
    except Exception as e:
        return internal_error(traceback.format_exc())


@app.route('/v1/chainhead', methods=["POST"])
def chainhead():
    """
    查询chain-head。 可以用来查询chainid是否存在
    params = {"chainid": chainid}
    """
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        chainid = params["chainid"]
        res, error = factom.get_chain_head(chainid)
        if error:
            return factom_error(error)
        return json_result(res)
    except Exception as e:
        return internal_error(traceback.format_exc())


@app.route('/v1/commit-chain', methods=["POST"])
def commit_chain_wtc():
    """
    创建chain
    params = {
        "extids": extids,
        "content": content,
        "ecpub": ecpub
    }
    extids = ["x", ...]
    """
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        extids, content = params["extids"], params["content"]
        ecpub = params.get("ecpub", Config.ECPUB)

        # 查询extids/chainid是否已经存在
        chainid = factom.nametoid(extids)
        res, error = get_chain_head(chainid)
        if res:
            return json_result({"message": "alreay exists!"})

        if error['code'] != -32009:  # Missing Chain Head
            return internal_error(error)

        # compose chain
        print("compose chain", chainid)
        res, error = get_compose_chain(ecpub, extids, content)
        if error:
            return factom_error(error)

        commit, reveal = res["commit"], res["reveal"]

        # commit chain
        print("commit chain")
        _, error = commit_chain(commit["params"]["message"])
        if error:
            if error["code"] != -32011:     # Repeated Commit
                return factom_error(error)

        time.sleep(2)

        # reveal chain
        print("reveal chain", reveal)
        reveal_res, error = reveal_chain(reveal["params"]["entry"])
        if error:
            return factom_error(error)

        return json_result({
            "chainid": reveal_res["chainid"],
            "entryhash": reveal_res["entryhash"],
        })
    except CustomError as e:
        return internal_error(e.error)
    except Exception as e:
        return internal_error(traceback.format_exc())


@app.route('/v1/commit-entry', methods=["POST"])
def commit_entry_wtc():
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
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        extids, chainid, content = params["extids"], params["chainid"], params["content"]
        ecpub = params.get("ecpub", Config.ECPUB)

        # 创建record, 并计算md5
        record = wtcrecord.make_wtc_record(**content)
        s = wtcrecord.encode_wtc_record(record)

        # compose entry
        res, error = get_compose_entry(ecpub, chainid, extids, s)
        if error:
            return factom_error(error)

        commit, reveal = res["commit"], res["reveal"]

        # commit entry
        _, error = commit_entry(commit["params"]["message"])
        if error:
            if error["code"] != -32011:  # Repeated Commit
                return factom_error(error)

        time.sleep(2)

        # reveal entry
        reveal_res, error = reveal_entry(reveal["params"]["entry"])
        # {'message': 'Entry Reveal Success', 'entryhash': '7c0401ef348aa8820babdc0c95e5a58ce4917a5b56da55a38fe7dd6a7ededb68', 'chainid': '46ba158332765c40c88f258b1b8650379b0b50f402f4504197eb6e313a5ec235'}
        if error:
            return factom_error(error)

        return json_result({
            "chainid": chainid,
            "entryhash": reveal_res["entryhash"],
        })
    except CustomError as e:
        return internal_error(e.error)
    except Exception as e:
        return internal_error(traceback.format_exc())


@app.route('/v1/entries', methods=["POST"])
def entries_wtc():
    def process(entrylist, result):
        for item in entrylist:
            entryhash = item["entryhash"]
            entry_res, error = get_entry(entryhash)
            if error:
                raise CustomError(error)

            content = entry_res["content"]
            try:
                # {'version': 1, 'md5': '6a08c9a28ddaed19df6ee9b07de02627', 'data': {'city': 'Ghuangzhou', 'ext': 850815, 'timestamp': 1517969082, 'desc': 'created at: 2018-02-07 02:04:42'}}
                record, error = wtcrecord.decode_wtc_record(unhex(content))     # decode并查检是否完整
                if record and wtcrecord.match_condition(record, condition):
                    result.append(entryhash)
            except Exception as e:
                traceback.print_exc()

    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        chainid, condition = params["chainid"], params["condition"]

        # 查检查询条件格式
        if not wtcrecord.is_condition_valid(condition):
            return invalid_param_error()

        # 获取chainid的head
        chainhead_res, error = get_chain_head(chainid)
        if error:
            return factom_error(error)

        result = []

        # 遍历子链
        chainhead = chainhead_res["chainhead"]
        while True:
            chaininprocesslist = chainhead_res["chaininprocesslist"]
            if chainhead == "" and chaininprocesslist:      # 还没写到块中，不处理
                continue

            # 获取entryblock
            entry_block_res, error = get_entry_block(chainhead)
            if error:
                return factom_error(error)

            header, entrylist = entry_block_res["header"], entry_block_res["entrylist"]
            chainhead = header["prevkeymr"]
            if chainhead == ZeroHash:       # 第一块是创建chain的块，不用处理
                break

            process(entrylist, result)      # 过滤
        return json_result({"entries":result})
    except CustomError as e:
        return internal_error(e.error)
    except Exception as e:
        return internal_error(traceback.format_exc())

@app.route('/v1/entry', methods=["POST"])
def entry_wtc():
    """
    检索一个entryhash对应的内容
    params = {"entryhash": entryhash}
    """
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        entryhash = params["entryhash"]
        entry_res, error = get_entry(entryhash)
        if error:
            return factom_error(error)

        extids, chainid, content = entry_res["extids"], entry_res["chainid"], entry_res["content"]
        return json_result({"extids": unhex(extids), "chainid": chainid, "content": unhex(content)})
    except CustomError as e:
        return internal_error(e.error)
    except Exception as e:
        return internal_error(traceback.format_exc())


@app.route('/v1/validate-entry', methods=["POST"])
def validate_entry_wtc():
    """
    到btc检验entryhash是否为真
    params = {"entryhash": entryhash}
    """
    jsonrpc = request.json
    try:
        params = jsonrpc["params"]
        entryhash = params["entryhash"]

        # 在factom查询receipt
        res, error = get_receipt(entryhash)
        if error:
            return factom_error(error)

        # 在factom校验receipt
        receipt_res = res["receipt"]
        _, error = validate_receipt(json.dumps(receipt_res))
        if error:
            return factom_error(error)

        # 检查factom是否anchor到btc上了
        bitcointransactionhash, bitcoinblockhash = receipt_res.get("bitcointransactionhash"), receipt_res.get("bitcoinblockhash")
        if not (bitcoinblockhash and bitcointransactionhash):
            return receipt_error("missing bitcoinblockhash/bitcointransactionhash!")

        # 去btc获取transaction的记录
        bitcoin_res, error = get_bitcoin_transaction(bitcointransactionhash)
        if error:
            return receipt_error(error)

        def get_data_hex(outputs):
            for output in outputs:
                data = output.get("data_hex")
                if data:
                    return data
            else:
                raise CustomError("missing data_hex")

        # 获取 op_return的内容： data_hex
        datahex = get_data_hex(bitcoin_res["outputs"])
        entryblockkeymr = receipt_res["entryblockkeymr"]
        directoryblockkeymr = receipt_res["directoryblockkeymr"]

        # 获取dbheight
        entryblock, error = get_entry_block(entryblockkeymr)
        if error:
            return blockchain_error("missing entryblockkeymr:" + entryblockkeymr)

        # 校验data_hex
        dbheight = entryblock["header"]["dbheight"]
        op_return = make_op_return_datahex(dbheight, directoryblockkeymr)
        if datahex != op_return:
            return blockchain_error("missmatch data_hex in btc")

        return json_result({"message": "success"})
    except CustomError as e:
        return internal_error(e.error)
    except Exception as e:
        return internal_error(traceback.format_exc())



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)