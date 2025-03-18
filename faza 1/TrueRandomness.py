import os

class TrueRandomness:
    NumBytes = 16
    already_used = False

    def __init__(self):
        pass

    @staticmethod
    def get():
        if TrueRandomness.already_used:
            raise ValueError("TrueRandomness already used")
        ret = os.urandom(TrueRandomness.NumBytes)
        TrueRandomness.already_used = True
        return ret
