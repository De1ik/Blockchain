import hmac
import hashlib

class PRF:
    KeySizeBits = 256
    KeySizeBytes = 32
    OutputSizeBits = 256
    OutputSizeBytes = 32
    AlgorithmName = "HmacSHA256"

    def __init__(self, prf_key):
        assert len(prf_key) == 32
        self.mac = hmac.new(prf_key, digestmod=hashlib.sha256)

    def eval(self, in_buf, in_offset=0, num_bytes=None, out_buf=None, out_offset=0):
        if num_bytes is None:
            num_bytes = len(in_buf) - in_offset
        self.mac.update(in_buf[in_offset:in_offset + num_bytes])
        return self.mac.digest()

    def eval_single(self, val, offset=0, num_bytes=None):
        try:
            ret = bytearray(32)
            self.eval(val, offset, num_bytes, ret)
            return ret
        except Exception as e:
            print(f"Error: {e}")
            return None
