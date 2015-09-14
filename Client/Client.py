'''
	client implementation
'''

import socket
import sys

class Client:
    def __init__(self, remote, port):
        self.remote = remote
        self.port = port
        self.sock = None

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def open_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.remote, self.port))

        return self.sock

    def send_message(self, message):
        try:
            self.sock = self.open_socket()
            self.sock.sendall(message)
            self.sock.close()
            return (True, '')
        except socket.error, (value, message):
            self.sock.close()
            return (False, message)
