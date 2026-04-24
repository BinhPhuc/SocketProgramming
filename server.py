import mimetypes
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote, urlsplit

from utils.load_config import app_config as config

PORT = config["server"]["port"]
BUFFER_SIZE = config["server"].get("buffer_size", 1024)
MAX_WORKERS = config["server"].get("max_workers", 4)
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"


def ensure_public_dir():
    PUBLIC_DIR.mkdir(exist_ok=True)


def receive_request(conn):
    request_data = b""

    while b"\r\n\r\n" not in request_data:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        request_data += chunk

    return request_data


def parse_requested_file(request_data):
    if not request_data:
        return None

    try:
        request_line = request_data.decode("utf-8", errors="ignore").splitlines()[0]
        _, raw_target, _ = request_line.split()
    except (IndexError, ValueError):
        return None

    request_path = unquote(urlsplit(raw_target).path).lstrip("/")
    if not request_path:
        return None

    candidate = (PUBLIC_DIR / request_path).resolve()
    try:
        candidate.relative_to(PUBLIC_DIR.resolve())
    except ValueError:
        return None

    return candidate


def build_response(status_code, reason, body, content_type="text/plain; charset=utf-8"):
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("utf-8") + body


def handle_client(conn, addr):
    with conn:
        request_data = receive_request(conn)
        file_path = parse_requested_file(request_data)

        if file_path and file_path.is_file():
            body = file_path.read_bytes()
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            response = build_response(200, "OK", body, content_type)
        else:
            response = build_response(404, "Not Found", b"404 Not Found")

        conn.sendall(response)
        print(f"Handled request from {addr}")


def main():
    ensure_public_dir()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor, socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", PORT))
        server_socket.listen(5)
        print(f"Server is listening on port {PORT} with {MAX_WORKERS} worker threads")

        while True:
            conn, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            executor.submit(handle_client, conn, addr)


if __name__ == "__main__":
    main()