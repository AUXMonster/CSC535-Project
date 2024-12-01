"""import aiohttp
import asyncio
import sys
import threading

async def wasteTime():
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://[{sys.argv[1]}]') as response:
                print("Status:", response.status)
                html = await response.text()
        return

async def main():
    for i in range(1000):
        asyncio.create_task(wasteTime())
    await asyncio.sleep(10)

asyncio.run(main())"""

import socket
import threading
import sys

def create_connection():
    try:
        sock = socket.create_connection((sys.argv[1], 80), timeout=1)
        sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        response = sock.recv(1024)
        # Do not close the socket immediately to simulate hanging connections
    except Exception as e:
        print(e)

threads = []

# Create a large number of threads to simulate concurrent connections
for _ in range(1000):
    thread = threading.Thread(target=create_connection)
    thread.start()
    threads.append(thread)

# Join threads to ensure all complete
for thread in threads:
    thread.join()
