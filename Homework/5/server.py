#!/usr/bin/env python3
import socket
import configparser
import sys
import logging
import requests
import json
from xml.dom import minidom
import threading
import daemon.runner
import time

key = "0f3049168af2ed1d55d73c559293f2f7"
sock = None
stop_state = False


def create_json(weather, n):
    out = []

    for i in range(n):
        timestamps = [i['main'] for i in weather['list'][i * 8: i * 8 + 7]]
        temp = sum((i['temp'] for i in timestamps)) / 8
        feel_like_temp = sum((i['feels_like'] for i in timestamps)) / 8
        date = weather['list'][i * 8]['dt_txt'].split()[0]
        out.append({'temp': temp, 'feels_like': feel_like_temp, 'date': date})

    out = {'list': out, 'city': {
            'name': weather['city']['name'],
            'country': weather['city']['country']
        }
    }

    return out


def check_code(code):
    if code == 200:
        logging.info("Got code 200, all OK")
        return 0
    elif code % 100 in (1, 2, 3):
        logging.info(f"Got code {code}")
        return 1
    else:
        logging.error(f"Error. Got code {code}")
        return 1


def create_xml(json_obj, n):
    doc = minidom.Document()
    root = doc.createElement("weather")
    doc.appendChild(root)

    for i in range(n):
        day = doc.createElement("day")
        root.appendChild(day)

        date = doc.createElement("date")
        day.appendChild(date)
        text = doc.createTextNode(str(json_obj['list'][i]['date']))
        date.appendChild(text)

        feels_like = doc.createElement("feels_like")
        day.appendChild(feels_like)
        text = doc.createTextNode(str(json_obj['list'][i]['feels_like']))
        feels_like.appendChild(text)

        temp = doc.createElement("temp")
        day.appendChild(temp)
        text = doc.createTextNode(str(json_obj['list'][i]['temp']))
        temp.appendChild(text)

    city = doc.createElement("city")
    root.appendChild(city)

    name = doc.createElement("name")
    city.appendChild(name)
    text = doc.createTextNode(str(json_obj['city']['name']))
    name.appendChild(text)

    country = doc.createElement("country")
    city.appendChild(country)
    text = doc.createTextNode(str(json_obj['city']['country']))
    country.appendChild(text)

    return root.toprettyxml(indent="    ")


def on_conn_established(client_socket: socket.socket, addr: str):
    global stop_state
    msg = client_socket.recv(1024).decode("utf-8")
    logging.info(f"New message '{msg}' received")

    if msg == "stop":
        client_socket.close()
        stop_state = True
        app.active = False
        app.prev_conn = time.time()
        return
    if not msg:
        client_socket.close()
        app.active = False
        app.prev_conn = time.time()
        return

    try:
        data = dict(map(lambda a: tuple(a.split('=')), msg.split('&')))
    except Exception:
        logging.error("Message could not be parsed")
        client_socket.send("Error! Wrong message".encode("utf-8"))
        client_socket.close()
        app.active = False
        app.prev_conn = time.time()
        return

    if 'q' not in data:
        logging.error("No querry in message")
        client_socket.send("No querry! Aborting!".encode("utf-8"))
        client_socket.close()
        app.active = False
        app.prev_conn = time.time()
        return
    if 'format' not in data:
        logging.error("No output format detected. Switching to JSON")
        data['format'] = 'json'

    querry = ("http://api.openweathermap.org/data/2.5/forecast?"
              f"q={data['q']}"
              "&mode=json"
              f"&cnt={int(data.get('n', '1')) * 8}"
              "&units=metric"
              f"&appid={key}")
    page = requests.get(querry)

    if check_code(page.status_code):
        client_socket.send("Oops! Something went wrong".encode("utf-8"))
        client_socket.close()
        app.active = False
        app.prev_conn = time.time()
        return

    n = int(data.get('n', '1'))
    weather = json.loads(page.content.decode("utf-8"))

    if 'list' not in weather:
        client_socket.send("Oops! Something went wrong".encode("utf-8"))
        client_socket.close()
        app.active = False
        app.prev_conn = time.time()
        return

    json_obj = create_json(weather, n)

    if data['format'] == 'json':
        client_socket.send(
            json.dumps(json_obj, indent=4, ensure_ascii=False).encode("utf-8")
        )
    else:
        json_obj = create_xml(json_obj, n)
        client_socket.sendall(json_obj.encode("utf-8"))

    client_socket.close()
    app.active = False
    app.prev_conn = time.time()
    return


class App:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(sys.argv[1])

    def run(self):
        port = int(self.config['DEFAULT']['port'])
        timeout = float(self.config['DEFAULT']['timeout'])
        connection_limit = int(self.config['DEFAULT']['connection_limit'])
        host = 'localhost'

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(connection_limit)
        sock.setblocking(False)

        self.prev_conn = time.time()
        self.active = False

        while not stop_state:
            if timeout > 0 and time.time() - self.prev_conn > timeout and\
                    not self.active:
                logging.error("Timed out")
                break

            try:
                conn, addr = sock.accept()
                self.active = True
            except BlockingIOError:
                continue

            threading._start_new_thread(on_conn_established, (conn, addr))

        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        logging.info("Server stopped!")


config = configparser.ConfigParser()
config.read(sys.argv[1])
is_daemon = int(config['ADDITIONAL'].get('daemon', 0))
log_path = config['ADDITIONAL'].get('log_path', None)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
handler = None

if not log_path:
    if is_daemon:
        print("Using default logger name './server.log' as"
              " stdout is unavailable for daemon")
        handler = logging.FileHandler("./server.log")
    else:
        handler = logging.StreamHandler(sys.stdout)
else:
    handler = logging.FileHandler(log_path)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = App()

if is_daemon:
    with daemon.DaemonContext(files_preserve=[handler.stream]):
        app.run()
else:
    app.run()
