import json
import struct
import hashlib


def make_wtc_record(**kwargs):
    m = dict()
    for (k, v) in kwargs.items():
        if isinstance(k, str) and isinstance(v, (int, str)):
            m[k] = v
        else:
            raise NotImplementedError("key shoud be str. value should be int/str")
    return m


def chksum(r):
    arr = [[k, v] for (k, v) in r.items()]

    barr = bytearray()
    for item in sorted(arr):
        v = item[1]
        if isinstance(v, int):
            barr.extend(struct.pack(">I", v))
        elif isinstance(v, str):
            barr.extend(v.encode())
        else:
            raise NotImplementedError("not support type " + str(type(v)))
    md5 = hashlib.md5(barr)
    return md5.hexdigest()


def encode_wtc_record(r):
    data = {
        "md5": chksum(r),
        "version": 1,
        "data": r
    }
    return json.dumps(data)


def decode_wtc_record(content):
    try:
        wtc_record = json.loads(content)
        version, r = wtc_record["version"], wtc_record["data"]
        if chksum(r) != wtc_record["md5"]:
            return None, "bad chksum"
        return make_wtc_record(**r), None
    except:
        return None, "bad record"

def is_condition_valid(condition):
    for (field, value) in condition.items():
        if not isinstance(field, str):
            return False
        if not isinstance(value, (str, int, list)):
            return False
        if isinstance(value, list):
            if len(value) != 2:
                return False
            min, max = value[0], value[1]
            if not (type(min) == type(max) and isinstance(min, (str, int))):
                return False
    return True

def match_condition(r, condition):
    """
        比较记录是否合法
        condition:
        {
            "city": "Shenzhen",
            "timestamp": [1, 1000],
            "ext": "none",
        }
    """
    for (field, value) in condition.items():
        v = r.get(field)
        if isinstance(value, list):
            min, max = value[0], value[1]

            if not (type(v) == type(min) == type(max)): # 比较类型
                return False
            if not (min <= v < max):    # 比较值
                return False
        else:
            if type(v) != type(value):   # 比较类型
                return False
            if v != value:      # 比较值
                return False
    return True

if __name__ == "__main__":
    content = encode_wtc_record(make_wtc_record(city="shenzhen", timestamp=2222))
    print(content)
    r = decode_wtc_record(content)
    print(r)