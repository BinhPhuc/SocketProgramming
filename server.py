import socket
import sys
from utils.load_config import app_config as config


PORT = config["server"]["port"]
HOST = None
s = None

for res in socket.getaddrinfo(
    HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE
):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(5)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print("could not open socket")
    sys.exit(1)
conn, addr = s.accept()
with conn:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        data = data.decode().upper()
        conn.send(data)
