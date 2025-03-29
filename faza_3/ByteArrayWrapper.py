class ByteArrayWrapper:
    def __init__(self, data):
        self.contents = bytes(data)

    def __eq__(self, other):
        return isinstance(other, ByteArrayWrapper) and self.contents == other.contents

    def __hash__(self):
        return hash(self.contents)
    