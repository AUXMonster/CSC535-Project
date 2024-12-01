import ipaddress
from Crypto.Cipher import Blowfish
from struct import pack

PRESHARED_KEY = b"I am a key. Bo!"
PRESHARED_IV = b"12345678"


def getFingerprintAddress(prefix, sourceAddress):
    sourceTop8 = int(sourceAddress).to_bytes(16)[:8]
    prefixTop8 = int(prefix).to_bytes(16)[:8]

    cipher = Blowfish.new(PRESHARED_KEY, Blowfish.MODE_CBC, PRESHARED_IV)
    fingerprint = cipher.encrypt(sourceTop8)

    fingerprintAddress = ipaddress.IPv6Address(prefixTop8 + fingerprint)
    return fingerprintAddress

def extractFingerprint(address):
    fingerprint = int(address).to_bytes(16)[8:]
    
    cipher = Blowfish.new(PRESHARED_KEY, Blowfish.MODE_CBC, PRESHARED_IV)
    cipherText = PRESHARED_IV + fingerprint
    sourceTop8 = cipher.decrypt(cipherText)[8:]

    subnet = ipaddress.IPv6Network((int.from_bytes(sourceTop8) << 64, 64))
    return subnet


"""
prefix = ipaddress.IPv6Address("FC00::")

sourceAddress = ipaddress.IPv6Address("0102:0304:0506:0708:abcd:aabb:ccdd:abcd")
print(sourceAddress)
fingerprintAddress = getFingerprintAddress(prefix, sourceAddress)
print(fingerprintAddress)
print(extractFingerprint(fingerprintAddress))
"""
