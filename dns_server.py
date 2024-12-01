import hashlib
import ipaddress
import http.server
import signal
import socketserver
import socket
import subprocess
import threading
import time
import ryanslib

PORT = 80
NAME = "mile-14.i75.iot.interstate.us"
SUBNET = ipaddress.IPv6Network("FC00::/64")

addrs = set()

class IOTEdgeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        fingerprint = ipaddress.IPv6Address(self.server.server_address[0])
        subnet = ryanslib.extractFingerprint(fingerprint)
        address = ipaddress.IPv6Address(self.client_address[0])
        if address not in subnet:
            print("Hacker!")
            print(f"{address} not in {subnet}")
            subprocess.run(["ip", "address", "delete", str(fingerprint), "dev", "lo"])
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(subnet).encode("utf-8"))

def CreateEndpoint(address):
    with Server((str(address), PORT), IOTEdgeHandler) as httpd:
        httpd.serve_forever()

class Server(socketserver.TCPServer):
    address_family = socket.AF_INET6
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_IP, 15, 1)
        super().server_bind()

class DNSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path != f"/dns-query?name={NAME}&type=AAAA":
            self.send_response(404)
            self.end_headers()
            return
        
        client_addr = ipaddress.ip_address(self.client_address[0])
        print(f"Client address: {client_addr}")
        address = ryanslib.getFingerprintAddress(SUBNET.network_address, client_addr)
       
        if address not in addrs:
            addrs.add(address)
            subprocess.run(["ip", "address", "add", str(address), "dev", "lo"])
            thread = threading.Thread(target = CreateEndpoint, args=(address,))
            thread.start()
        
        response = f'{{"Answer": [{{"name":"{NAME}","type":28,"TTL":128,"data":"{address}"}}]}}'
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))
        return

try:
    with Server((str(next(SUBNET.hosts())), PORT), DNSHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt as e:
    for addr in addrs:
        subprocess.run(["ip", "address", "delete", str(addr), "dev", "lo"])
