import socket
from utils.load_config import app_config as config

PORT = config["server"]["port"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen(5)
    print(f"Server is listening on port {PORT}")
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            data = data.upper()
            conn.send(data)
