from hashlib import sha256
def nametoid(extids):
    ba = bytearray()
    for name in extids:
        ba.extend(sha256(name.encode()).digest())

    return sha256(ba).hexdigest()
