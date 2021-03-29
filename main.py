import socket
from views import return_405, return_404, index
import config
import sys
import logging
from typing import Optional, Any


def logging_configure(debug_level: Optional[int] = logging.ERROR) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(config.LOGGER_NAME)
    # Logger format with level, time and message
    formatter: logging.Formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s')
    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(debug_level)
    return logger


api_logger: logging.Logger = logging_configure(logging.DEBUG if config.DEBUG else logging.ERROR)

URLS: dict = {
    '/': index,
}


def parse_request(request: Optional[str]) -> tuple[str, str, dict]:
    parsed: list = request.split()
    method: str = parsed[0]
    parsed: list = parsed[1].split('?')
    url = parsed[0]
    if len(parsed) != 2:
        params: Any[dict, list] = {}
    else:
        params = parsed[1].split('&')
        params = {i.split('=')[0]: i.split('=')[1] for i in params if len(i.split('=')) == 2}
    return method, url, params


def generate_headers(method: str, url: str) -> tuple[str, int]:
    if not method == 'GET':
        return 'HTTP/1.1 405 Method not allowed\n\n', 405
    if url not in URLS:
        return 'HTTP/1.1 404 Not found\n\n', 404

    return 'HTTP/1.1 200 OK\n\n', 200


def generate_content(code: int, url: str, kwargs: dict, headers: str) -> tuple[str, str]:
    if code == 404:                                     # If url not in list then 404
        return headers, return_404()
    if code == 405:                                     # If not GET method
        return headers, return_405()
    return URLS[url](headers, **kwargs)


def generate_response(request: Optional[str]) -> bytes:
    method: str
    url: str
    kwargs: dict
    code: int
    body: str
    method, url, kwargs = parse_request(request)
    headers, code = generate_headers(method, url)
    headers, body = generate_content(code, url, kwargs, headers)
    response = (headers + body).encode()
    api_logger.debug('Response:\n' + headers + body)
    return response


def run() -> None:
    # Create socket
    server_socket: socket.socket = socket.socket(socket.AF_INET,    # Which protocol should be used (SOCK_STREAM = TCP))
                                                 socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                             1)  # sudo fuser -k 5000/tcp  - to delete port
    server_socket.bind((config.SERVER_ADDRESS, config.SERVER_PORT))
    # Listening the created socket
    server_socket.listen()
    do_run: bool = True
    api_logger.debug('Server listening...')
    while do_run:
        clint_socket: Optional[socket.socket] = None
        addr: tuple[str, int]
        try:
            clint_socket, addr = server_socket.accept()  # Return tuple which unpacks into two variables
            # Return socket from client
            request: Any[bytes, str] = clint_socket.recv(1024)  # 1024 - bites in packet
            if request:
                request = request.decode('utf-8')
                api_logger.debug('Request:\n' + str(request.rstrip()))
                response: bytes = generate_response(request)
                clint_socket.sendall(response)
        except IOError as e:
            api_logger.exception(e)
            continue
        except KeyboardInterrupt:
            if clint_socket:
                clint_socket.close()
            break
        except Exception as e:
            api_logger.exception(e)


if __name__ == '__main__':
    run()
