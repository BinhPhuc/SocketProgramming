import socket
import sys
from utils.load_config import app_config as config

PORT = config["server"]["port"]
HOST = config["server"]["host"]

s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print("could not open socket")
    sys.exit(1)
with s:
    msg = input("Enter message to send: ")
    s.sendall(msg.encode())
    data = s.recv(1024)
print("Received", repr(data))
