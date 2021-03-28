import socket
from views import return_405, return_404, index
import config
import sys
from utils import error_json
import logging


def logging_configure(bebug_level=logging.ERROR):
    logger = logging.getLogger(config.LOGGER_NAME)
    formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(bebug_level)
    return logger


api_logger = logging_configure(logging.DEBUG if config.DEBUG else logging.ERROR)

URLS = {
    '/': index,
}


def parse_request(request):
    parsed = request.split()
    method = parsed[0]
    parsed = parsed[1].split('?')
    url = parsed[0]
    if len(parsed) != 2:
        params = {}
    else:
        params = parsed[1].split('&')
        params = {i.split('=')[0]: i.split('=')[1] for i in params if len(i.split('=')) == 2}
    return method, url, params


def generate_headers(method, url):
    if not method == 'GET':
        return 'HTTP/1.1 405 Method not allowed\n\n', 405  # отделяем заголовок от тела

    if url not in URLS:
        return 'HTTP/1.1 404 Not found\n\n', 404

    return 'HTTP/1.1 200 OK\n\n', 200


def generate_content(code, url, kwargs, headers):
    if code == 404:
        return headers, return_404()
    if code == 405:
        return headers, return_405()
    return URLS[url](headers, **kwargs)


def generate_response(request):
    method, url, kwargs = parse_request(request)
    headers, code = generate_headers(method, url)  # если url не тот, то 404, если method, то др. заголовок
    headers, body = generate_content(code, url, kwargs, headers)
    response = (headers + body).encode()
    api_logger.debug('Response:\n' + headers + body)
    return response


def run():
    # создаем субъекта
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # указали, какой протокол будет исп-ть.
    # AF_INET - протокол 4-й версии
    # SOCK_STREAM - TCP протокол
    # Связываем субъекта с конкретным IP:port
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # опции (на каком уровне SOlevel, переисп. адрес устан. в 1 (не SO_REUSEADDR))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                             1)  # sudo fuser -k 5000/tcp            - удаляем порт

    server_socket.bind((config.SERVER_ADDRESS, config.SERVER_PORT))  # картеж
    # Теперь нужно сказать: чувак, давай, тебе могут придти пакеты, иди посмотри
    server_socket.listen()
    do_run = True
    api_logger.debug('Server listening...')
    while do_run:
        clint_socket = None
        try:
            clint_socket, addr = server_socket.accept()  # возвращает картеж, кот. распаковываем в 2-е переменные
            # возвращает сокет, но со сороны клиенты
            request = clint_socket.recv(1024)  # 1024 - кол-во байт в пакете
            if request:
                request = request.decode('utf-8')
                api_logger.debug('Request:\n' + str(request.rstrip()))
                response = generate_response(request)  # декодируем все таки, т.к. приходит в браузер
                clint_socket.sendall(response)  # преобразовываем из строки с bytes
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
