import socket
import requests
import signal
import os
import sys
from typing import Optional, List
from multiprocessing import Process
from multiprocessing.connection import Pipe


def worker(conn: Connection):
    while True:
        url = conn.recv()
        # TODO: Logic


def sig_handler(sigcode, frame):
    if sigcode == signal.SIGUSR1:
        for process in processes:
            process.terminate()

def master():
    

processes: Optional[List[Process]] = None

if __name__ == "__main__":
    print(f"[INFO] Server PID: {os.getpid()}")
    signal.signal(signal.SIGUSR1, sig_handler)

    n_workers = int(sys.argv[1])

    connections = [
        Pipe() for _ in range(n_workers)
    ]
    processes = [
        Process(target=worker, args=(conn[0],))
        for conn in connections
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()
