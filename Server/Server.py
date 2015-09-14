'''
    server implementation
'''

import select
import socket
import sys
import threading
from SynchronizedList import SList

class Server(threading.Thread):
    def __init__(self, host, port):
        self.init_values(host, port)

    def init_values(self, host, port):
        self.list = SList()
        self.host = host
        self.port = port
        self.threads = []
        threading.Thread.__init__(self)

    def new_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "ERROR: Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.new_socket()
        selector = [self.server, sys.stdin]
        running = 1
        while running:
            inready, outready, exceptready = select.select(selector, [], [])

            for s in inready:
                if s == self.server:
                    c = Client(self.server.accept(), self.list)
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    running = 0

        self.server.close()
        for c in self.threads:
            c.join()


        for name, host, port in self.list.get_list():
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.sendall('#terminated')
                sock.close()
            except socket.error, (value, message):
                print 'ERROR: [' + host + ':' + str(port) + ']' + message
                sock.close()

        print "INFO: Server stopped"

class Client(threading.Thread):
    def __init__(self, (client,address), lst):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.lst = lst

    def run(self):
        data = self.client.recv(self.size)
        if data:
            self.parse_data(data)

    def parse_data(self, data):
        """
            #register user host port
        """
        if data.startswith('#register'):
            reg_tokens = data.split(' ')
            if len(reg_tokens) < 4:
                print 'ERROR: Fatal Error! Invalid message'
                return

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((reg_tokens[2], int(reg_tokens[3])))

            self.lst.lock_list()

            for name, host, port in self.lst.get_list():
                if name == reg_tokens[1]:
                    sock.sendall('#addfail already a user with this name')
                    sock.close()
                    print 'ERROR: username ' + reg_tokens[1] + ' already registered'
                    return

                if host == reg_tokens[2] and port == int(reg_tokens[3]):
                    for i, (dname,dhost,dport) in enumerate(self.lst.get_list()):
                        if dname == name and dport == port and dhost == host:
                            del self.lst.get_list()[i]

                    sock.sendall('#modifyok')
                    sock.close()

                    for nname,nhost,nport in self.lst.get_list():
                        self.send_message(nhost,nport,data)

                    self.lst.add((reg_tokens[1], host, port))

                    self.lst.unlock_list()
                    return




            self.lst.unlock_list()

            self.lst.add((reg_tokens[1], reg_tokens[2], int(reg_tokens[3])))

            ret_mes = '#addok'
            print 'INFO: succesfully added user ' + reg_tokens[1]

            self.lst.lock_list()
            for name, host, port in self.lst.get_list():
                if not name.startswith(reg_tokens[1]):
                    ret_mes += '\n' + name + ' ' + host + ' ' + str(port)
                    self.send_message(host, port, data)

            self.lst.unlock_list()

            sock.sendall(ret_mes)
            sock.close()

        elif data.startswith('#modify'):
            ret_mes = ''
            mod_tokens = data.split(' ')
            oname = mod_tokens[1]
            nname = mod_tokens[2]

            self.lst.lock_list()
            for el in self.lst.get_list():
                name, host, port = el
                if name == nname:
                    ret_mes = '#modifyfail already a user with this name'

            if ret_mes == '':
                for el in self.lst.get_list():
                    name, host, port = el
                    if name == oname:
                        new_el = nname, host, port
                        self.lst.remove(el)
                        self.lst.add(new_el)

                        self.send_message(host, port, '#modifyok')
                        print 'INFO: Succesfully changed name from [' + oname + '] to [' + nname + '] listening on [' + host + ':' + str(port) + ']'
                    else:
                        self.send_message(host, port, data)

            else:
                for name,host,port in self.lst.get_list():
                    if name == oname:
                        self.send_message(host, port, ret_mes)

                print 'ERROR: ' + ret_mes

            self.lst.unlock_list()



        elif data.startswith('#message'):
            mes_tokens = data.split(' ')
            if len(mes_tokens) < 2:
                print 'ERROR: invalid #message format'
                return None

            self.lst.lock_list()

            for name, host, port in self.lst.get_list():
                if name == mes_tokens[1]:
                    continue
                self.send_message(host, port, data)

            print 'DBG: received message from [' + mes_tokens[1] + ']'

            self.lst.unlock_list()

        elif data.startswith('#unregister'):
            ureg_toks = data.split(' ')

            self.lst.lock_list()

            for el in self.lst.get_list():
                name, host, port = el
                if name == ureg_toks[1]:
                    self.lst.remove(el)
                else:
                    self.send_message(host, port, data)

            self.lst.unlock_list()

            print 'INFO: user [' + ureg_toks[1] + '] leaved the room'

        else:
            print 'ERROR: Unknown message'

    def send_message(self, host, port, message):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(message)
            sock.close()
        except socket.error, (value, message):
            print 'ERROR: [' + host + ':' + str(port) + ']' + message
            sock.close()


def main():
    host = '127.0.0.1'
    port = 8001
    if len(sys.argv) > 1:
        host = sys.argv[1]
        if len(sys.argv) > 1:
            port = int(sys.argv[2])

    print 'Server started! Running on ' + host + ':' + str(port)

    server = Server(host, port)
    server.start()


if __name__ == '__main__':
    main()
