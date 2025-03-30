from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import binascii


class RSAHelper:
    def __init__(self, key_size=2048):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        self.public_key = self.private_key.public_key()

    def sign(self, message: bytes) -> bytes:
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def sign_multisig(self, message: bytes, private_keys: list) -> list:
        signatures = []
        for key in private_keys:
            signature = key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            signatures.append(signature)
        return signatures

    @staticmethod
    def verify(public_key, message: bytes, signature: bytes) -> bool:
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    @staticmethod
    def verify_multisig(public_keys: list, message: bytes, signatures: list, required: int) -> bool:
        valid_signatures = 0

        for public_key in public_keys:
            for signature in signatures:
                try:
                    public_key.verify(
                        signature,
                        message,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    valid_signatures += 1
                    break
                except:
                    continue

        return valid_signatures >= required

    @staticmethod
    def get_short_address(public_key, length=16):
        key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        digest = hashes.Hash(hashes.SHA256())
        digest.update(key_bytes)
        key_hash = digest.finalize()

        short_address = binascii.hexlify(key_hash)[:length].decode("utf-8")
        return short_address
