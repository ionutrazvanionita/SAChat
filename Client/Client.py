'''
	client implementation
'''

import socket
import sys

class Client:
    def __init__(self, remote, port):
        self.remote = remote
        self.port = port

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def open_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.remote, self.port))

        return sock

    #TODO there s a bug here on error
    def send_message(self, message):
        try:
            sock = self.open_socket()
            sock.sendall(message)
            sock.close()
        except socket.error, (value, message):
            print "Failed to send"
            sock.close()
            sys.exit(1)
