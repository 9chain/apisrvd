from .common import make_data, common_factom_request


def factomd_request(data):
    return common_factom_request("http://localhost:8088/v2", data=data)

def get_chain_head(chainid):
    """
    {
        "chainhead": "3afddcb46e644bd8e8edae4e506d894322c9fa4ba2c61625861df7ee3485e387",
        "chaininprocesslist": false
    }
    """
    return factomd_request(make_data(method="chain-head", params={"chainid": chainid}))

def get_entry_block(chainhead):
    """
    {
        "header": {
          "blocksequencenumber": 11,
          "chainid": "4d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0",
          "prevkeymr": "e6463e070243b6eb1874d44e70098263a3a2f3968682b86ba92d0c24cf366ad6",
          "timestamp": 1517646000,
          "dbheight": 8404
        },
        "entrylist": [
          {
            "entryhash": "df22b74afb94344e63bd48f1c6cab63d8f45010fee8debc4760df003997f258f",
            "timestamp": 1517646120
          },
          {
            "entryhash": "1d5a67c0721001cf3ace85c9ea2e32ec69048deb7f9e1ae30396257685889002",
            "timestamp": 1517646300
          },
          {
            "entryhash": "7e6010bd4dbd025f065f9d9d8ba245f534d92dc7010da80d5fae78693625df4f",
            "timestamp": 1517646480
          }
        ]
    }
    """
    return factomd_request(make_data(method="entry-block", params={"keymr": chainhead}))


def get_entry(entryhash):
    """
    {
        "chainid": "4d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0",
        "content": "7b2264657363223a20224265696a696e67222c2022657874223a2022313039222c202274696d657374616d70223a2022323031382d30322d30332031333a32303a3130222c202263697479223a20224265696a696e67227d",
        "extids": [
          "746573742065787469642039"
        ]
    }
    """
    return factomd_request(make_data(method="entry", params={"hash": entryhash}))

def get_entry_status(entryhash):
    """
    {
      "commitdata": {
        "status": "DBlockConfirmed"
      },
      "entrydata": {
        "status": ""
      },
      "committxid": "5f4c94576ed78bf90dfae23c6b83af6c07e6f9eae3d0f7d7be999d52f90a9382",
      "entryhash": ""
    }
    """
    return factomd_request(make_data(method="ack", params={"hash": entryhash, "chainid":"c"}))

def commit_entry(message):
    """
    {
        "message": "Entry Commit Success",
        "txid": "47d2993c23f82d6200354cc0fee1c6e5c671a03360d02de3b9db3dc1582ae1a2",
        "entryhash": "fef71575252a969d57f49c2e6c87062451bebd84ff9da2ebae877a29ffdcb0cc"
    }
    """
    return factomd_request(make_data(method="commit-entry", params={"message": message}))

def reveal_entry(entry):
    """
    {
        "message": "Entry Reveal Success",
        "entryhash": "fef71575252a969d57f49c2e6c87062451bebd84ff9da2ebae877a29ffdcb0cc",
        "chainid": "4d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0"
    }
    """
    return factomd_request(make_data(method="reveal-entry", params={"entry": entry}))

def get_receipt(entryhash):
    """
    {
      "receipt": {
        "entryblockkeymr": "d8440a817c26cb631b0bd130663b74ab5106269f104d51a9413372b8da1f1d6c",
        "directoryblockkeymr": "c5b33f5de7f52da0179e86076d8696ca46fc5c9bf06d57600bcaa82b7c9e52fa",
        "entry": {
          "entryhash": "1370af59343edb8b5402759baacf2ec7e04643f886626b0fcee0276f7ef039ec"
        },
        "merklebranch": [
          {
            "right": "0000000000000000000000000000000000000000000000000000000000000009",
            "top": "0daa475a92b80b074451813eb0d42c4405aa243642205a3c3b6a88637e18c9d4",
            "left": "1370af59343edb8b5402759baacf2ec7e04643f886626b0fcee0276f7ef039ec"
          },
          {
            "right": "0daa475a92b80b074451813eb0d42c4405aa243642205a3c3b6a88637e18c9d4",
            "top": "d8440a817c26cb631b0bd130663b74ab5106269f104d51a9413372b8da1f1d6c",
            "left": "3bd9181ae8c0c9c4b1cd8bee418d0f8a5c00506bf2f59256fd481095bc05ff2e"
          },
          {
            "right": "d8440a817c26cb631b0bd130663b74ab5106269f104d51a9413372b8da1f1d6c",
            "top": "fb6ba0d8019af3120cb0b81f08671fb1d18b70eb40e8b604d2eb54caf691f59b",
            "left": "4d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0"
          },
          {
            "right": "fb6ba0d8019af3120cb0b81f08671fb1d18b70eb40e8b604d2eb54caf691f59b",
            "top": "afcf98857c668b0572041ab42a9e6b59f663385f09fbade2689faa014d2e4be2",
            "left": "bb8b031ce7a287c06557f024fd6c39bceab6d639b23e8112ee00905c3d4ea373"
          },
          {
            "right": "afcf98857c668b0572041ab42a9e6b59f663385f09fbade2689faa014d2e4be2",
            "top": "f21204a8fbc65050012a564b8d38d83f5a7f61a0223d9e96d4b57be749bb2cd0",
            "left": "4599c81b850f7527b9f7e8ca1d04bb36b1d7525cf29375a637acff4da6e64031"
          },
          {
            "right": "f21204a8fbc65050012a564b8d38d83f5a7f61a0223d9e96d4b57be749bb2cd0",
            "top": "c5b33f5de7f52da0179e86076d8696ca46fc5c9bf06d57600bcaa82b7c9e52fa",
            "left": "5533cac1291bef70a54e9610b134d7c0bffd2d80f5fefafa7e77869978f203a7"
          }
        ]
      }
    }
    {'code': -32010, 'message': 'Receipt creation error'}
    """
    return factomd_request(data=make_data(method="receipt", params={"hash": entryhash}))

def validate_receipt(receipt):
    return factomd_request(data=make_data(method="validate-receipt", params={"receipt": receipt}))

def commit_chain(message):
    """
    {
      "txid": "5c1bcb8a63234e867f2ca09bfd2f920de9ae39f11711ea1672cedbaad1072232",
      "chainidhash": "55009473beebb61a5518ae5ef0a46ebb5bce2104893216fc0ee860ed9572aa80",
      "message": "Chain Commit Success",
      "entryhash": "ac251327d8471a880152fc5a23732fb75c6c7f6e053e9f503696baf203440df7"
    }
    """
    return factomd_request(make_data(method="commit-chain", params={"message": message}))

def reveal_chain(entry):
    """
    {
      "message": "Entry Reveal Success",
      "entryhash": "ac251327d8471a880152fc5a23732fb75c6c7f6e053e9f503696baf203440df7",
      "chainid": "67c3fcb84aa38cc2d72c43f48668150cfb00d7ea75a4ce16839d078a2ec02709"
    }
    """
    return factomd_request(make_data(method="reveal-chain", params={"entry": entry}))
