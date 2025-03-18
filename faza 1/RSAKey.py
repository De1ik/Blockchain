import os
import PRGen, TrueRandomness, PRF

class RSAKey:
    NUM_ZERO_BYTES = 16
    NUM_RANDOM_BYTES = 16
    MARKER_BYTE = 1
    gen = None
    h = None

    @staticmethod
    def initialize():
        # Create an instance of TrueRandomness and get randomness
        TrueRandomness.TrueRandomness()  # Ensures it has been used
        randomness = TrueRandomness.TrueRandomness.get()

        # Pad randomness to 32 bytes
        padded_randomness = RSAKey.pad(randomness, 32, False)

        # Initialize PRGen and PRF
        RSAKey.gen = PRGen.PRGen(padded_randomness)
        key = bytearray(32)  # Create a 32-byte array for the key
        RSAKey.h = PRF.PRF(key)

    def __init__(self, exponent, modulus):
        if exponent is not None and modulus is not None:
            self.exponent = exponent
            self.modulus = modulus
        else:
            raise ValueError("Exponent or Modulus cannot be None")

    def encrypt(self, plaintext):
        if plaintext is None:
            raise ValueError("Plaintext cannot be None")
        if self.max_plaintext_length() == 0:
            raise ValueError("Modulus is too small for any plaintext")
        if len(plaintext) > self.max_plaintext_length():
            raise ValueError(f"Plaintext can be at most {self.max_plaintext_length()} bytes")
        oaep_output = self.oaep(plaintext)
        encrypted = pow(int.from_bytes(oaep_output, byteorder='big'), self.exponent, self.modulus)
        return encrypted.to_bytes((encrypted.bit_length() + 7) // 8, byteorder='big')

    def get_exponent(self):
        return self.exponent

    def get_modulus(self):
        return self.modulus

    def decrypt(self, ciphertext):
        if ciphertext is None:
            raise ValueError("Ciphertext cannot be None")
        if self.max_plaintext_length() == 0:
            raise ValueError("Modulus is too small for any plaintext")
        encrypted = int.from_bytes(ciphertext, byteorder='big')
        oaep_input = pow(encrypted, self.exponent, self.modulus)
        return self.oaep_reverse(oaep_input.to_bytes((oaep_input.bit_length() + 7) // 8, byteorder='big'))

    def sign(self, message):
        if message is None:
            raise ValueError("Message cannot be None")
        if self.max_plaintext_length() < 32:
            raise ValueError("Modulus is too small for a digital signature")
        hashed = self.h.eval(message)
        return self.encrypt(hashed)

    def verify_signature(self, message, signature):
        if message is not None and signature is not None:
            if self.max_plaintext_length() < 32:
                raise ValueError("Modulus is too small for a digital signature")
            hashed = self.h.eval(message)
            decrypted_signature = self.decrypt(signature)
            if decrypted_signature is None:
                return False
            if len(hashed) != len(decrypted_signature):
                return False
            return hashed == decrypted_signature
        else:
            raise ValueError("Message or Signature cannot be None")

    def max_plaintext_length(self):
        max_len = (self.modulus.bit_length() - 1) // 8 - 16 - 16 - 2
        return max_len if max_len >= 0 else 0

    def oaep(self, plaintext):
        if plaintext is None:
            raise ValueError("Plaintext cannot be None")
        padded = self.pad(plaintext, self.max_plaintext_length() + 1, True)
        left1 = self.pad(padded, len(padded) + 16, False)
        right_random = os.urandom(16)
        right1 = self.pad(right_random, 32, False)
        prg = PRGen.PRGen(right1)
        g_output = bytearray(len(left1))
        prg.next(8 * len(g_output))
        left2 = self.xor(left1, g_output)
        h_output = self.h.eval(left2)
        h_output_cropped = h_output[:16]
        right2 = self.xor(h_output_cropped, right_random)
        output = bytearray(len(left2) + len(right2) + 1)
        output[0] = 1
        output[1:len(left2) + 1] = left2
        output[len(left2) + 1:] = right2
        return output

    def oaep_reverse(self, input_data):
        if input_data is None:
            raise ValueError("Input cannot be None")
        if len(input_data) != self.max_plaintext_length() + 16 + 16 + 2:
            return None
        left2 = input_data[1:len(input_data) - 16 - 1]
        right2 = input_data[len(left2) + 1:]
        h_output = self.h.eval(left2)
        h_output_cropped = h_output[:16]
        right_random = self.xor(h_output_cropped, right2)
        right1 = self.pad(right_random, 32, False)
        prg = PRGen.PRGen(right1)
        g_output = bytearray(len(left2))
        prg.next(8 * len(g_output))
        left1 = self.xor(left2, g_output)
        for i in range(len(left1) - 16, len(left1)):
            if left1[i] != 0:
                return None
        return self.unpad(left1)

    def xor(self, a, b):
        if len(a) != len(b):
            raise ValueError("a and b must have the same length")
        return bytes([ai ^ bi for ai, bi in zip(a, b)])

    @staticmethod
    def pad(a, length, marker):
        if length < len(a):
            raise ValueError("Length must be >= len(a)")
        padded = bytearray(length)
        padded[:len(a)] = a
        if marker:
            padded[len(a)] = 1
        return bytes(padded)

    def unpad(self, a):
        for i in range(len(a) - 1, -1, -1):
            if a[i] != 0:
                return a[:i+1]
        raise ValueError("a is nothing but padding")
