import argparse
import socket
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Request a file from the HTTP socket server."
    )
    parser.add_argument("server_host", help="Hostname or IP address of the server")
    parser.add_argument("server_port", type=int, help="Port number of the server")
    parser.add_argument("filename", help="File path to request from the public directory")
    return parser.parse_args()


def build_request(server_host, filename):
    normalized_path = "/" + filename.lstrip("/")
    request_lines = [
        f"GET {normalized_path} HTTP/1.1",
        f"Host: {server_host}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(request_lines).encode("utf-8")


def receive_response(sock):
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    return response


def parse_response(response):
    header_bytes, _, body = response.partition(b"\r\n\r\n")
    header_text = header_bytes.decode("utf-8", errors="ignore")
    header_lines = header_text.split("\r\n") if header_text else []
    status_line = header_lines[0] if header_lines else ""

    headers = {}
    for line in header_lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    return status_line, headers, body


def is_text_content(content_type):
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type.startswith("text/") or media_type in {
        "application/json",
        "application/javascript",
        "application/xml",
    }


def print_text_content(body):
    print(body.decode("utf-8", errors="replace"))


def save_file(filename, content):
    output_path = Path(filename).name
    output_path = Path(output_path)
    output_path.write_bytes(content)
    return output_path


def main():
    args = parse_args()
    request = build_request(args.server_host, args.filename)

    print(f"Connecting to server at {args.server_host}:{args.server_port}...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((args.server_host, args.server_port))
            sock.sendall(request)
            response = receive_response(sock)
    except OSError as exc:
        print(f"Connection failed: {exc}")
        return

    status_line, headers, body = parse_response(response)

    if "200 OK" in status_line:
        content_type = headers.get("content-type", "")
        if is_text_content(content_type):
            print_text_content(body)
        else:
            saved_path = save_file(args.filename, body)
            print(f"Downloaded file to {saved_path}")
    else:
        print(status_line or "Invalid response from server")
        if body:
            print(body.decode("utf-8", errors="ignore"))


if __name__ == "__main__":
    main()
