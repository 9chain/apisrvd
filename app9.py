
from flask import Flask, request
import functools
import requests
import json

from factom.exceptions import *

fct_address = 'FA2jK2HcLnRdS94dEcU27rF3meoJfpUcZPSinpb7AwQvPRY6RL1Q'
ec_address = 'EC2jhmCtabeTXGtuLi3AaPzvwSuqksdVsjfxXMXV5gPmipXc4GjC'


app = Flask(__name__)

ApiKeyMap = {
    "test": "apikey"
}

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


def invalid_request(id):
    CODE = -32600
    MESSAGE = "Invalid Request"
    return json.dumps({"jsonrpc": "2.0", "id": id or 0, "error": {"message": MESSAGE, "code": CODE}})


class InvalidParamException(Exception):
    CODE = -32602
    MESSAGE = "Invalid params"
    def __init__(self, data=None):
        self.data = data


class CustomException(Exception):
    def __init__(self, CODE, MESSAGE, data=None):
        self.data = data
        self.CODE = CODE
        self.MESSAGE = MESSAGE

dispatcher = dict()
@app.route('/v1', methods=["POST","GET"])
def application():
    # Dispatcher is dictionary {<method_name>: callable}
    # dispatcher["echo"] = lambda s: s
    # dispatcher["add"] = lambda a, b: a + b

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
            return invalid_request(0)

        if not (method and jsonrpc and params):
            return invalid_request(id)

        func = dispatcher.get(method)
        if not func:
            CODE = -32601
            MESSAGE = "Method not found"
            err = {"jsonrpc": "2.0", "id": id, "error": {"message": MESSAGE, "code": CODE}}
            return json.dumps(err)
        result = func(params)
        return json.dumps({"jsonrpc": "2.0", "id": id, "result": result})
    except (TypeError, ValueError):
        CODE = -32700
        MESSAGE = "Parse error"
        return json.dumps({"jsonrpc": "2.0", "id": 0, "error": {"message": MESSAGE, "code": CODE}})
    except InvalidParamException as e:
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": {"message": e.MESSAGE, "code": e.CODE, "data": e.data}})
    except CustomException as e:
        return json.dumps({"jsonrpc": "2.0", "id": id, "error": {"message": e.MESSAGE, "code": e.CODE, "data": e.data}})
    except Exception as e :
        CODE = -32603
        MESSAGE = "Internal error"
        print(e)
        return json.dumps({"jsonrpc": "2.0", "id": 0, "error": {"message": MESSAGE, "code": CODE}})


def addmethod(method):
    def inner_dec(f):
        dispatcher[method] = f
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(args, kwargs)

        return wrapped
    return inner_dec


@addmethod("create-entry")
def create_entry(*args, **kwargs):
    print(args)
    print(kwargs)
    return kwargs


def invalidParams(message="Invalid params", data=None, code=-32602):
    return json.dumps({"jsonrpc": "2.0", "id": 0, "error": {"message": message, "code": code, "data": data}})


@addmethod("entry")
def entry(params):
    entryhash = params.get("hash")
    if not entryhash:
        raise InvalidParamException()

    try:
        result = factomd.entry(entryhash)
        content = result["content"]
        return {"content": utils.unhex(content)}
    except BlockNotFound as e:
        raise CustomException(e.code, e.message, e.data)


@addmethod("validate")
def validate(*args, **kwargs):
    pass


@addmethod("status")
def status(params):
    entryhash = params.get("hash")
    if not entryhash:
        raise InvalidParamException()

    try:
        result = factomd.ac(entryhash)
        content = result["content"]
        return {"content": utils.unhex(content)}
    except BlockNotFound as e:
        raise CustomException(e.code, e.message, e.data)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)