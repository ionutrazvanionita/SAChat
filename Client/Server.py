'''
    server implementation
'''

import select
import socket
import sys
import threading
import random
import Helpers

class Server(threading.Thread):
    def __init__(self, host, port, lst, gui):
        self.init_values(host, port, lst, gui)

    def set_gui(self, gui):
        self.gui = gui

    def init_values(self, host, port, lst, gui):
        self.host = host
        self.port = port
        self.threads = []
        self.lst = lst
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.gui = gui

    def new_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.gui.displayInfo('Listening on [' + self.host + ':' + str(self.port) + ']')
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            self.server = None
            self.gui.displayErr('[' + self.host + ':' +str(self.port) + '] ' + message)

    def run(self):
        self.new_socket()
        if self.server == None:
            return

        selector = [self.server, sys.stdin]
        self.running = 1
        while self.running:
            inready, outready, exceptready = select.select(selector, [], [], 1)

            for s in inready:
                if s == self.server:
                    c = Client(self.server.accept(), self.lst, self.lock, self.gui)
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    self.running = 0

        self.server.close()
        for c in self.threads:
            c.join()

    def stop_server(self):
        self.running = 0

class Client(threading.Thread):
    """
    """
    def __init__(self, (client,address), lst, lock, gui):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.lst = lst
        self.lock = lock
        self.gui = gui

    def run(self):
        data = self.client.recv(self.size)
        if data:
            self.process_data(data)
        self.client.close()

    def process_data(self, data):
        #registration request
        if data.startswith('#register'):
        #simple message
            userColor =Helpers.genSixDigitHex()

            tokens = data.split(' ')
            with self.lst.get_lock():
                self.lst.add((tokens[1],tokens[2], int(tokens[3]), userColor))
            if self.gui != None:
                with self.lock:
                    self.gui.display_user(tokens[1])

        elif data.startswith('#message'):
            # #message user message
            new_tokens = data.split(' ')
            if self.gui != None:
                user = new_tokens[1]
                mes = data[len('#message ' + user + ' '):]

                with self.lst.get_lock():
                    for luser, lip, lport, lcolor in self.lst.list:
                        if user == luser:
                            userColor = lcolor
                            break



                with self.lock:
                    self.gui.display_line(user, mes, userColor)
        elif data.startswith('#addok'):
            with self.lock:
                self.gui.display_success()

            users = data.split('\n')

            with self.lock:
                self.gui.display_user(None)

            if len(users) < 2:
                return

            for urow in users[1:]:
                utoks = urow.split(' ')
                ucolor = Helpers.genSixDigitHex()
                with self.lst.get_lock():
                    self.lst.add((utoks[0], utoks[1], utoks[2], ucolor))

                with self.lock:
                    self.gui.display_user(utoks[0])


        elif data.startswith('#modifyok'):
            with self.lock:
                self.gui.display_modify()
        elif data.startswith('#modifyfail'):
            pass
        elif data.startswith('#addfail'):
            pass
        elif data.startswith('#unregister'):
            unreg_toks = data.split(' ')

            with self.lst.get_lock():
                for el in self.lst.get_list():
                    name, host, port, color = el
                    if name == unreg_toks[1]:
                        self.lst.remove(el)
                        with self.lock:
                            self.gui.displayInfo('user <b>' + unreg_toks[1] + '</b> exited')
                            self.gui.remove_user(unreg_toks[1])

        else:
            with self.gui.lock:
                self.gui.displayBug('<b>BUG:</b> unknown request [' + data + ']')

