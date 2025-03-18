import random
from sympy import isprime, mod_inverse
from RSAKey import RSAKey


class RSAKeyPair:
    E = 65537

    def __init__(self, rand, num_bits):
        if rand is None:
            raise ValueError("Random generator cannot be None")
        if num_bits <= 0:
            raise ValueError("numBits must be positive")

        self.p = self.generate_prime(rand, num_bits)
        self.q = self.generate_prime(rand, num_bits)
        self.N = self.p * self.q
        secret_mod = (self.p - 1) * (self.q - 1)

        while self.N <= self.E:
            self.p = self.generate_prime(rand, num_bits)
            self.q = self.generate_prime(rand, num_bits)
            self.N = self.p * self.q
            secret_mod = (self.p - 1) * (self.q - 1)

        self.D = mod_inverse(self.E, secret_mod)
        RSAKey.initialize()
        self.public_key = RSAKey(self.E, self.N)
        self.private_key = RSAKey(self.D, self.N)

    def generate_prime(self, rand, num_bits):
        while True:
            prime = random.getrandbits(num_bits)
            if isprime(prime):
                return prime

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_primes(self):
        return [self.p, self.q]
