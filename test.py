#!/usr/bin/env python
import time
import requests
import json
from testconfig import Config

class CustomError(RuntimeError):
    def __init__(self, error):
        self.error = error

def wtc_request(*, method, data):
    url = "{}/v1/{}".format(Config.HOST, method)
    jsondata = {"params":data, "jsonrpc": "2.0", "id": 0, "method":method}
    res = requests.post(url, json=jsondata, headers={'content-type': 'application/json'})
    print(url)
    print(json.dumps(jsondata))
    s = res.content.decode()
    print(s)
    res = json.loads(s)
    error = res.get("error")
    if error:
        print(error)
        raise CustomError(error)
    return res["result"]

def create_chain_wtc2(ec_address = Config.ECPUB, extids = Config.CHAIN_EXTIDS, content = Config.CHAIN_CONENT):
    data = {
        "extids": extids,
        "content": content,
        # "ecpub": ec_address
    }
    return wtc_request(method="commit-chain", data=data)

def create_entry_wtc2(chainid = None, ecpub = Config.ECPUB, extids = None, content = None):
    data = {
        "chainid": chainid,
        "extids": extids,
        "content": content,
        # "ecpub": ecpub
    }
    return wtc_request(method="commit-entry", data=data)


def entry_validate(entryhash = None):
    entryhash = entryhash if entryhash else "0ae2ab2cf543eed52a13a5a405bded712444cc8f8b6724a00602e1c8550a4ec2"
    return wtc_request(method="validate-entry", data={"entryhash": entryhash})


def get_chain_id(extids=Config.CHAIN_EXTIDS):
    extids = extids if extids else ["demo_chain"]
    return wtc_request(method="nametoid", data={"extids": extids})


def get_chain_head(chainid=None):
    chainid = chainid if chainid else "b33cf828690aa5a01de9a6bccd241f0b4bf6ad65980995b5fd957481ec892be8"
    res = wtc_request(method="chainhead", data={"chainid": chainid})
    print("chainhead")
    print(res)


def entries_wtc(chainid = None, condition = None):
    chainid = chainid if chainid else "4d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0"
    condition = condition if condition else {
      # "city": "Shenzhen",
        "city": "Shanghai",
        "timestamp": [0, 2517930488]
    }

    data = {
        "chainid": chainid,
        "condition": condition,
    }

    return wtc_request(method="entries", data=data)


def test_create_chain():
    # 创建子链
    res = create_chain_wtc2(extids=Config.CHAIN_EXTIDS)
    print("commit-chain")
    print(res)


def test_create_entry():
    cities = ["Beijing", "Shenzhen", "Ghuangzhou", "Nanjing", "Chongqing", "Shanghai", "Xiamen"]
    import random


    idx = random.randint(0, len(cities) - 1)
    city = cities[idx]

    r = {
        "timestamp": int(time.time()),
        "city": city,
        "desc": "created at: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "ext": random.randint(0, 10000000)
    }

    chainid_res = get_chain_id(Config.CHAIN_EXTIDS)
    chainid = chainid_res["chainid"]
    extids = [city, str(idx)]

    print("create entry at chainid:", chainid, extids)

    entry_res = create_entry_wtc2(chainid=chainid, extids=extids, content=r)
    print("commit-entry")
    print(entry_res)

def get_entry(entryhash):
    data = {
        "entryhash": entryhash,
    }

    return wtc_request(method="entry", data=data)

def test_query_entries():
    chainid_res = get_chain_id(Config.CHAIN_EXTIDS)
    chainid = chainid_res["chainid"]
    res = entries_wtc(chainid, {
        # "city": "Ghuangzhou",
        "timestamp": [1, 1517986136]
    })
    print("entries_wtc")
    print(res)
    for entryhash in res["entries"]:
        res = get_entry(entryhash)
        print("entry")
        print(res)

def test1():
    test_create_chain()

    # 根据子链名称获取子链chainid TODO 要手动设置（可能使用命令不能及时获取，此时请手动设置）
    # 创建一个entry
    # test_create_entry()
    # get_chain_head()
    # test_query_entries()

    # 验真：还没完成
    # res = entry_validate("3e5d59a2a236fa284039a43469fdcfe479e59a6f407948369d5863393330162a")
    # res = entry_validate("808a46ca19a08d0e5ccef5f0432bf064408a62f802faaaf6aa91c46f590e1b9c")
    # print(res)
    pass


if __name__ == "__main__":
    try:
        test1()
    except CustomError as e:
        print("custom error", e.error)
    except Exception as e:
        print("error")
        print(e)
