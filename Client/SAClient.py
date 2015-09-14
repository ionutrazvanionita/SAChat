"""
	SAChat Client
"""


import Server
import Client
import socket
from SynchronizedList import SList
import sys

class SAClient:
    def __init__(self, host=None, port=None, remote_host=None, remote_port=None, gui = None):
        self.list = SList()
        self.gui = gui

        if host != None and port != None:
            self.init_server(host, port)
        else:
            self.server = None
        if remote_host != None and remote_port != None:
            self.init_client(remote_host, remote_port)
        else:
            self.client = None

    def init_server(self, host, port):
        if self.server != None:
            self.server.stop_server()

        self.server = Server.Server(host, port, self.list, self.gui)
        self.server.start()

    def init_client(self, remote_host, remote_port):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.client = Client.Client(remote_host, remote_port)


    def get_reomote_host(self):
        return self.remote_host

    def get_remote_port(self):
        return self.remote_port

    def send_message(self, message):
        return self.client.send_message(message)

