#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import SAClient
import socket
import random


class SAChat(QtGui.QWidget):

    def __init__(self):
        super(SAChat, self).__init__()

        self.port = None
        self.host = None
        self.client = SAClient.SAClient(None, None,None,None,self)

        self.initUI()

        self.username = None
        self.olduser = None
        self.chatEdit.append("Type #help for list of available commands")
        self.chatEdit.append("<b>IMPORTANT: </b>Before connecting to a server you must set your listening interface with #listen")

    def display_help(self):
        self.chatEdit.append("#help")
        self.chatEdit.append("    #register <user> <remote_host> <remote_port> - connect to chat server")
        self.chatEdit.append("    #clear - clears message history")
        self.chatEdit.append("    #listen <host> <port> - set ip and andress where to receive messages")
        self.chatEdit.append("    #logout - logs out from the current server")

    def parse_text(self):
        chatStr = str(self.sendEdit.displayText())
        if chatStr.startswith('#help'):
            self.display_help()
            self.sendEdit.clear()
            return

        if chatStr.startswith('#listen'):
            tokens = chatStr.split(' ')
            if len(tokens) != 3:
                self.chatEdit.append("syntax: #listen <ip> <port>")
                return

            port = int(tokens[2])
            addr = tokens[1]
            try:
                socket.inet_aton(addr)
            except socket.error:
                self.chatEdit.append("invalid ip address")

            self.host = addr
            self.port = port

            self.client.init_server(addr, port)
            self.sendEdit.clear()

            return

        if chatStr.startswith('#register'):
            reg_tokens = chatStr.split(' ')
            if len(reg_tokens) != 4:
                self.chatEdit.append("syntax: #register <user> <ip> <port>")
                return

            if self.username != None:
                self.chatEdit.append("changing username to <b>" +reg_tokens[1] + "</b>")
                mes = '#modify ' + self.username + ' ' + reg_tokens[1]
                self.olduser = self.username
                self.username = reg_tokens[1]
            else:
                mes = reg_tokens[0] + ' ' + reg_tokens[1]
                mes += ' ' + self.host + ' ' + str(self.port)
                self.username = reg_tokens[1]


            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((reg_tokens[2], int(reg_tokens[3])))

            sock.sendall(mes)
            sock.close()
            self.sendEdit.clear()

            self.client.init_client(reg_tokens[2], int(reg_tokens[3]))

            return
        if chatStr.startswith('#logout'):
            self.logOut()
            self.sendEdit.clear()

            return

        if chatStr.startswith('#clear'):
            self.chatEdit.clear()
            self.sendEdit.clear()

            self.chatEdit.append("Type #help for list of available commands")
            return

        if chatStr != '':
            self.sendEdit.clear()
            if self.client.client == None:
                self.chatEdit.append('<font color=\'red\'><b></b>You must register to a server with <b>#register</b>')
                return
            self.client.client.send_message('#message ' + self.username + ' ' + chatStr)
            self.chatEdit.append("<b>You : </b> " + chatStr)

    def logOut(self):
        if self.client.client != None:
            self.client.client.send_message('#unregister ' + self.username)
            self.onlineUsers.clear()
            self.client.client = None
            self.chatEdit.append('Succesfully logged out')

        else:
            self.chatEdit.append('Not connected to a server')

        self.username = None
        self.olduser  = None

    def onSendClicked(self):
		self.parse_text()

    def onSendEnterPressed(self, e):
		self.parse_text()

    def onAddUser(self, user):
        color = random.randint(0, 255*255*255)
        if color < 255*255*16:
            color += 255*255*16

        colorstr = "<font color=\"#"+ str(hex(color))[2:]+"\">"

        icon = QtGui.QIcon('online.ico')
        item = QtGui.QListWidgetItem(user)
        item.setIcon(icon)
        self.onlineUsers.addItem(item)

        self.chatEdit.append(colorstr + "user <b>" + user + "</b> is now online")

    def onNewMessage(self, user, line, color):
        colorstr = "<font color=\"#"+ color[2:] + "\">"

        printstr = colorstr + '<b>' + user + ':</b><\\font> ' + line
        self.chatEdit.append(printstr)

    def onOkRegister(self):
        self.chatEdit.append('registered with username <b>' + self.username + '<\b>')

    def onModify(self):
        color = random.randint(0, 255*255*255)
        if color < 16*255*255:
            color += 16 * 255 * 255;
        colorstr = "<font color=\"#"+ (hex(color))[2:]+"\">"

        self.chatEdit.append(colorstr + 'succesfully changed name to <b>' + self.username + '</b>')

        for idx in xrange(self.onlineUsers.count()):
            item = self.onlineUsers.item(idx)
            if item.text() == self.olduser:
                item.setText(self.username)


    def onLog(self, mes):
        self.chatEdit.append(mes)

    def onUserExit(self, user):
        for idx in xrange(self.onlineUsers.count()):
            item = self.onlineUsers.item(idx)
            if item.text() == user:
                self.onlineUsers.takeItem(idx)
                return

    def display_user(self, user):
        if user == None:
            user = self.username

        self.emit(QtCore.SIGNAL('onAddUser(QString)'), user)

    def remove_user(self, user):
        self.emit(QtCore.SIGNAL('onUserExit(QString)'), user)

    def display_line(self, user, line, color):
        self.emit(QtCore.SIGNAL('onNewMessage(QString,QString,QString)'), user, line, color)

    def display_success(self):
        self.emit(QtCore.SIGNAL('onOkRegister()'))

    def display_log(self, mes):
        self.emit(QtCore.SIGNAL('onLog(QString)'), mes)

    def display_modify(self):
        self.emit(QtCore.SIGNAL('onModify()'))

    def initUI(self):
        self.chatEdit = QtGui.QTextEdit()

        self.onlineUsers = QtGui.QListWidget()

        self.chatEdit.setReadOnly(True)
#        self.onlineUsers.setReadOnly(True)

        self.sendEdit = SendLineEdit()


        self.sendButton = QtGui.QPushButton("Send")
        QtCore.QObject.connect(self.sendButton, QtCore.SIGNAL('clicked()'), self.onSendClicked)

        QtCore.QObject.connect(self.sendEdit, QtCore.SIGNAL('returnPressed'), self.onSendClicked)

        QtCore.QObject.connect(self, QtCore.SIGNAL('onAddUser(QString)'), self.onAddUser)

        QtCore.QObject.connect(self, QtCore.SIGNAL('onNewMessage(QString, QString, QString)'), self.onNewMessage)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onOkRegister()'), self.onOkRegister)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onLog(QString)'), self.onLog)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onModify()'), self.onModify)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onUserExit(QString)'), self.onUserExit)


        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.sendEdit, 4, 0)

        self.grid.addWidget(self.chatEdit, 1, 0)
        self.grid.addWidget(self.onlineUsers, 1, 3, 1, 4)

        self.grid.addWidget(self.sendButton, 4, 4)

        self.setLayout(self.grid)

        self.setGeometry(300, 300, 750, 500)
        self.setWindowTitle('Chat')
        self.show()

    def closeEvent(self, event):
        if self.client.client != None:
            self.client.client.send_message('#unregister ' + self.username)

        event.accept()



class SendLineEdit(QtGui.QLineEdit):
    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)

    def event(self, event):
        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Return):
            self.emit(QtCore.SIGNAL('returnPressed'))
            return True

        return QtGui.QLineEdit.event(self, event)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = SAChat()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
