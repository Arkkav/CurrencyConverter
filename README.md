## Конвертор валют
### Техническое задание
Реализовать простой сервис конвертации валют USD -> RUB. Интерфейс - HTTP API, который по запросу отдает JSON с результатом конвертации (валюта, запрошенное значение, результирующее значение, и т.д.) или ошибкой с соответствующим кодом и сообщением в секции “error”.

### Имплементация
Реализовано на "чистом" python, без использования зависимостей и сторонних библиотек.
Код покрыт тестами, помещен в docker-контейнер, действия логгируются, используется опциональная типизация.
Источник данных - любой веб-ресурс на выбор. Данные парсятся с web страницы.
Использованные стандартные библиотеки:
- threading
- json
- urllib
- time
- logging
- sys
- socket
- html
- functools

#### Основные модули
- config.py - файл конфигурации
- main.py - основной модуль обработки запроса и реализации сервера
- utils.py - модуль вспомогательных функций и классов
- views.py - модуль представлений
- test.py - автоматические тесты

### Установка приложения 
```bash
mkdir CurrencyConverter
git clone https://github.com/Arkkav/CurrencyConverter.git CurrencyConverter
cd CurrencyConverter
python3.9 -m venv venv
. venv/bin/activate

#sudo docker build -t my-docker-image .
```
CTRL+C для выхода 

### Запуск сервиса
```
 python main.py
``` 
Запуск Docker контейнера:
```bash
#sudo docker run --rm -it --name my-docker-instance -p 8000:5000 my-docker-image
#sudo fuser -k 80/tcp  # если нужно освободить порт

``` 

### Запуск автотестов
```
python -m unittest
python -m unittest tests.test.CurrencyConverterTest.test_get_page  # для запуска 
``` 
### Пример использования

---
GET /?amount=14 HTTP/1.1
Host: 0.0.0.0:8000

HTTP/1.1 200 OK
{"Currency": "USD", "Amount": "14", "Rate": "76.1741", "Result": "1066.4374"}
---
GET / HTTP/1.1
Host: 0.0.0.0:8000

HTTP/1.1 400 Amount parameter not found
{"Error": "Amount parameter not found."}
---
GET /?amount=wfewfe HTTP/1.1
Host: 0.0.0.0:8000

HTTP/1.1 400 Amount should be float
{"Error": "Amount should be float."}