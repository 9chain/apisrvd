
import json
from factom import CustomError, CustomError2
# {"jsonrpc": "2.0", "result": 19,"id": 1}
# {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "1"}


def json_error(code, message, data=None):
    error = dict(code=code, message=message)
    if data:
        error["data"] = data
    print(1111111111, error)
    raise CustomError2(error)
    # return json.dumps({"jsonrpc": "2.0", "id":1, "error": error})


def factom_error(error):
    # return json.dumps({"jsonrpc": "2.0", "id": 1, "error": error})
    raise CustomError(error)