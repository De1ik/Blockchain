import random
from PRF import PRF


class PRGen(random.Random):
    KeySizeBytes = 32
    KeySizeBits = 256

    def __init__(self, key):
        super().__init__()
        if key and len(key) == 32:
            self.key = bytearray(32)
            self.key[:32] = key
        else:
            raise ValueError("Invalid key")

    def next(self, bits):
        if 1 <= bits <= 32:
            prf = PRF(self.key)
            zero = bytearray([0])
            one = bytearray([1])
            out = prf.eval(zero)
            self.key = prf.eval(one)
            full = (out[0] & 255) << 24 | (out[1] & 255) << 16 | (out[2] & 255) << 8 | out[3] & 255
            return full if bits == 32 else full & (1 << bits) - 1
        else:
            raise ValueError("Bits must be between 1 and 32")
