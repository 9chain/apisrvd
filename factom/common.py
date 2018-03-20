import json
import requests


class CustomError(RuntimeError):
    def __init__(self, error):
        self.error = error


class CustomError2(RuntimeError):
    def __init__(self, error):
        self.error = error



def make_data(*, method, params, id=0):
    return json.dumps({
        "jsonrpc": "2.0",
        "id": id,
        "method": method,
        "params": params
    })


def common_factom_request(url, data):
    res = requests.post(url, data=data, headers={'content-type': 'application/json'})
    s = res.content.decode()
    res = json.loads(s)
    return res.get("result"), res.get("error")
