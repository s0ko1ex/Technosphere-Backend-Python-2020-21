import socket
from multiprocessing import Pool
import sys


def send_url(url: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, port = 'localhost', 61000
    sock.connect((host, port))
    sock.sendall(url.encode("utf-8"))

    data = sock.recv(1024)
    sock.close()

    print(data.decode("utf-8"))


if __name__ == "__main__":
    filename, m = sys.argv[1], int(sys.argv[2])
    urls = None
    with open(filename, "r") as file:
        urls = file.readlines()

    with Pool(m) as p:
        p.map(send_url, urls)
