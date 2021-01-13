#!/usr/bin/env python3
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = 'localhost'
port = 61000

sock.connect((host, port))
sock.sendall(sys.argv[1].encode("utf-8"))

print(sock.recv(1024).decode("utf-8"))
sock.close()
