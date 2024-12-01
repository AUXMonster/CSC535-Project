import ipaddress
import random
import requests
from requests_toolbelt.adapters import source
import socket
import subprocess
import time
import json

NETWORK = ipaddress.IPv6Network("FC00::/64")

HOST = "FC00::1"
PORT = 80
NUMBER = random.randint(0, 2**64)

def getAddress(network):
    number = random.randint(0, 2**48) << 64
    addr = network.network_address + number
    return addr


ADDRESS = getAddress(NETWORK)
subprocess.run(["ip", "address", "add", f"{ADDRESS}", "dev", "lo"])

try:
    print(str(ADDRESS))
    source = source.SourceAddressAdapter(str(ADDRESS))
    with requests.Session() as session:
        session.mount("http://", source)
        r = session.get("http://[FC00::1]:80/dns-query?name=mile-14.i75.iot.interstate.us&type=AAAA")
        t = r.text
        address = ipaddress.IPv6Address(json.loads(t)["Answer"][0]["data"])
        print(address)
        while True:
            time.sleep(1)
            r = session.get(f"http://[{address}]")
            print(r.status_code)
except Exception as e:
    print(e)


"""
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, 15, 1)
    s.bind((str(ADDRESS), 0))
    s.connect((HOST, PORT))
    s.sendall(b"GET / HTTP/1.1\n\n")
    data = s.recv(64000)
    print(repr(data))
"""

subprocess.run(["ip", "address", "delete", f"{ADDRESS}", "dev", "lo"])
