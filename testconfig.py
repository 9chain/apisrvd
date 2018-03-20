class BaseConfig:
    HOST = "http://127.0.0.1:6000"
    ECPUB = "EC2NG6CMgf2EprnEvFobSnxkrSfSco1YJ6YhD9WGMRCSRe4ngXnF"
    CHAIN_EXTIDS = ["demo_chain"]
    CHAIN_CONENT = "testx"


# 可自定義配置，
class Test1Config(BaseConfig):
    CHAIN_EXTIDS = ["my_test_chain10"]
    # ECPUB = "EC3dn6DeUDtZu1YgVC31W5FDVJYhfP6Z3abvbEsbfmLqfma6rMnN"  # empty


# test.py中使用的配置
Config = Test1Config