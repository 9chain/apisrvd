from .common import make_data, common_factom_request
from hexlib import hex

def factom_walletd_request(data):
    return common_factom_request("http://localhost:8089/v2", data=data)


def get_compose_chain(ecpub, extids, content):
    """
    {
    "commit": {
      "jsonrpc": "2.0",
      "id": 209,
      "params": {
        "message": "000161604d6c1e55009473beebb61a5518ae5ef0a46ebb5bce2104893216fc0ee860ed9572aa800abae54b0e9ae5769537a036dc45134292188f0f9318630fd12110dc4f2baf1eac251327d8471a880152fc5a23732fb75c6c7f6e053e9f503696baf203440df70b4fb815ea51801b66bda5b14282a5d66624ec0fb55296d97baae57fe08eaf07486789d7717b9cc50af084021776b893028b537240606ee9f38d3f5c740ded6bea8bce07c7605e4e4ec99447cc0f171b4e767206ec123dd02e728eceb0dddfc20a"
      },
      "method": "commit-chain"
    },
    "reveal": {
      "jsonrpc": "2.0",
      "id": 210,
      "params": {
        "entry": "0067c3fcb84aa38cc2d72c43f48668150cfb00d7ea75a4ce16839d078a2ec02709000c000a7465737420636861696e7b226669656c6473223a5b7b226669656c64223a2263697479222c2274797065223a2274657874227d2c7b226669656c64223a2274696d657374616d70222c2274797065223a22696e74227d2c7b226669656c64223a2264657363222c2274797065223a2274657874227d2c7b226669656c64223a22657874222c2274797065223a2274657874227d5d7d"
      },
      "method": "reveal-chain"
    }
    }
    """
    return factom_walletd_request(make_data(method="compose-chain", params={
        "chain": {
          "firstentry": {
            "extids": hex(extids),
            "content": hex(content)
          }
        },
        "ecpub": ecpub
      }))


def get_compose_entry(ecpub, chainid, extids, content):
    """
    {
        "commit": {
          "jsonrpc": "2.0",
          "id": 43,
          "params": {
            "message": "0001615aa20ab5fef71575252a969d57f49c2e6c87062451bebd84ff9da2ebae877a29ffdcb0cc014fb815ea51801b66bda5b14282a5d66624ec0fb55296d97baae57fe08eaf0748d5d671b2998907264875a97185ea047d7238f7861b972cf1fadf58572d07098d40f774494550967a7e0b9ff61afdc56cd265fc0ab2e1f3b20c59fdd8e9115506"
          },
          "method": "commit-entry"
        },
        "reveal": {
          "jsonrpc": "2.0",
          "id": 44,
          "params": {
            "entry": "004d13b0ef34d6b80c22573ffd65ab7029919ced55cbc53f666b224e459ef463b0000a0008656e7472796964317b2263697479223a225368656e7a68656e222c2264657363223a2264656d6f222c2274696d657374616d70223a22323031382d30322d30332031323a30313a3130222c22657874223a22313031227d"
          },
          "method": "reveal-entry"
        }
    }
    """
    return factom_walletd_request(make_data(method="compose-entry", params={
        "entry": {
            "chainid": chainid,
            "extids": hex(extids),
            "content": hex(content)
        },
        "ecpub": ecpub
    }))
