import socket
from utils.load_config import app_config as config

PORT = config["server"]["port"]
HOST = config["server"]["host"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        msg = input("Enter message to send. Type 'exit' to quit: ")
        if msg.lower() == 'exit':
            break
        s.sendall(msg.encode())
        data = s.recv(1024).decode()
        print("Received", data)
