#!/usr/bin/env python

import socket
import threading
import select
import sys
import os
import syslog
import signal
import errno

LISTEN_IP   = "0.0.0.0"
LISTEN_PORT = 8080

SERVER_IP   = "103.43.149.148"
SERVER_PORT = 80

HTT_PROXY   = "10.10.10.10:8080"

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

if __name__ == '__main__':

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((LISTEN_IP, LISTEN_PORT))
    serverSocket.listen(20)

    while True:
        try:
            print ("Waiting for client...")
            clientSocket, address = serverSocket.accept()
        except socket.error as (code, msg):
            if code != errno.EINTR:
                raise
            continue
        except KeyboardInterrupt:
            print ("Terminating...")
            terminateAll = True
            break

        print ("accept new connection from {}".format(address))
        newpid = os.fork()
        if newpid == 0:
            os.dup2(clientSocket.fileno(), 0)
            os.dup2(clientSocket.fileno(), 1)
            os.execlp("nc", "nc", "-X", "connect", "-x", HTT_PROXY, SERVER_IP, "{}".format(SERVER_PORT))
        else:
            pids = (os.getpid(), newpid)
           #print ("parent: %d, child: %d\n" % pids)
        clientSocket.close()
       #ClientThread(clientSocket, address).start()

    print ("serverSocket terminating")
    serverSocket.close()
