#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import SAClient
import socket
import random
import Helpers
import Analyzer

class SAChat(QtGui.QWidget):

    def __init__(self):
        super(SAChat, self).__init__()

        self.port = None
        self.host = None
        self.client = SAClient.SAClient(None, None,None,None,self)
        self.holder = Helpers.WidgetHolder()
        self.analyzer = Analyzer.Parser()

        self.initUI()

        self.username = None
        self.olduser = None
        Helpers.printHelpInfo(self.holder.getChatWindow())
        Helpers.printListenInfo(self.holder.getChatWindow())

        self.command_hist = []
        self.command_idx = 0


    def display_help(self):
        Helpers.printHelpMessage(self.holder.getChatWindow())

    def parse_text(self):
        chatStr = self.holder.getWrittenMessageAndClear()
        if len(self.command_hist) == 10:
            self.command_hist = self.command_hist[1:]

        self.command_hist.append(str(chatStr))
        self.command_idx = len(self.command_hist) - 1

        if chatStr.startswith('#help'):
            self.display_help()
            return

        if chatStr.startswith('#listen'):
            tokens = chatStr.split(' ')
            if len(tokens) != 3:
                self.holder.writeLog("""syntax: #listen ip port""", self.holder.LEVEL_WARN)
                return

            port = int(tokens[2])
            addr = tokens[1]
            try:
                socket.inet_aton(addr)
            except socket.error, (value, message):
                self.holder.writeLog(message, self.holder.LEVEL_ERR)

            self.host = addr
            self.port = port

            self.client.init_server(addr, port)
            return

        if chatStr.startswith('#register'):
            reg_tokens = chatStr.split(' ')
            if len(reg_tokens) != 4:
                self.holder.writeLog("""syntax: #register user ip port""", self.holder.LEVEL_WARN)
                return

            if  self.client.server == None:
                self.holder.writeLog("""must set listening interface first with #listen""", self.holder.LEVEL_ERR)
                return


            mes = reg_tokens[0] + ' ' + reg_tokens[1]
            mes += ' ' + self.host + ' ' + str(self.port)
            self.olduser = self.username
            self.username = reg_tokens[1]

            if self.username == self.olduser:
                self.onError('New username must differ from old one')
                return

            self.client.init_client(reg_tokens[2], int(reg_tokens[3]))
            err,mes = self.client.send_message(mes)

            if err == False:
                self.onError(mes)

            return
        if chatStr.startswith('#logout'):
            self.logOut()

            return

        if chatStr.startswith('#clear'):
            self.holder.clearChatWindow()
            self.holder.writeLog("Type #help for list of available commands", self.holder.LEVEL_INFO)
            return

        if chatStr.startswith('#exit') or chatStr.startswith('#quit'):
            if self.client.client != None:
                err,mess = self.client.client.send_message('#unregister ' + self.username)
                if err == False:
                    self.onError(mes)
                    return

            if self.client.server != None:
                self.client.server.stop_server()

            QtCore.QCoreApplication.instance().quit()

            return

        if chatStr != '':
            if self.client.client == None:
               self.holder.writeLog('You must register to a server with <b>#register</b>', self.holder.LEVEL_WARN)
               return
            err,mes = self.client.client.send_message('#message ' + self.username + ' ' + chatStr)
            if err == False:
                self.onError(mes)
                return

            self.holder.writeMessage("<b>You : </b> " + chatStr)
            scores = self.analyzer.get_score_for_phrase(chatStr)
            for s in self.analyzer.depeche_sents:
                if s in scores:
                    self.holder.set_pbar_value(s, scores[s])
                else:
                    self.holder.set_pbar_value(s, 0)

    def logOut(self):
        if self.client.client != None:
            err,mess = self.client.client.send_message('#unregister ' + self.username)
            if err == False:
                self.onError(mes)
                return
            self.holder.clearStatusWindow()
            self.client.client = None
            self.holder.writeLog('Succesfully logged out', self.holder.LEVEL_INFO)

        else:
            self.holder.writeLog('Not connected to a server', self.holder.LEVEL_INFO)

        self.username = None
        self.olduser  = None


    def initUI(self):
        self.initWidgets()
        self.initSignals()

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        self.placeWidgets()

        self.setLayout(self.grid)

        self.setGeometry(300, 300, 750, 500)
        self.setWindowTitle('SAChat')
        self.show()

    def initSignals(self):
        QtCore.QObject.connect(self.holder.getSendButton(), QtCore.SIGNAL('clicked()'), self.onSendClicked)
        QtCore.QObject.connect(self.holder.getSendWindow(), QtCore.SIGNAL('returnPressed'), self.onSendClicked)
        QtCore.QObject.connect(self.holder.getSendWindow(), QtCore.SIGNAL('upPressed'), self.onUpArrow)
        QtCore.QObject.connect(self.holder.getSendWindow(), QtCore.SIGNAL('downPressed'), self.onDownArrow)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onAddUser(QString)'), self.onAddUser)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onNewMessage(QString, QString, QString)'), self.onNewMessage)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onOkRegister()'), self.onOkRegister)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onModify()'), self.onModify)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onUserExit(QString)'), self.onUserExit)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onServerExit()'), self.onServerExit)

        #log signals
        QtCore.QObject.connect(self, QtCore.SIGNAL('onErr(QString)'), self.onError)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onInfo(QString)'), self.onInfo)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onWarn(QString)'), self.onWarn)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onBug(QString)'), self.onBug)
        QtCore.QObject.connect(self, QtCore.SIGNAL('onDbg(QString)'), self.onDbg)

    def initWidgets(self):
        self.holder.setChatWindow(QtGui.QTextEdit())
        self.holder.setStatusWindow(QtGui.QListWidget())
        self.holder.setSendWindow(SendLineEdit())
        self.holder.setSendButton(QtGui.QPushButton('Send'))

        self.holder.getChatWindow().setReadOnly(True)
        for s in self.analyzer.depeche_sents:
            self.holder.set_pbar(s, QtGui.QProgressBar())

    def placeWidgets(self):
        box = QtGui.QVBoxLayout()

        box.addWidget(QtGui.QLabel("<b>Emotion Analyser</b>\t"))
        for s in self.analyzer.depeche_sents:
            box.addWidget(QtGui.QLabel(Helpers.fontWithRandColor() + "<i>" + s + "</i>"))
            box.addWidget(self.holder.get_pbar(s))


        self.grid.addWidget(self.holder.getSendWindow(), 4, 0)
        self.grid.addWidget(self.holder.getChatWindow(), 1, 0)
        self.grid.addWidget(self.holder.getStatusWindow(), 1, 1, 1, 2)
        self.grid.addWidget(self.holder.getSendButton(), 4, 1)
        self.grid.addLayout(box, 0, 4, 2, 4)

    def closeEvent(self, event):
        if self.client.client != None:
            err, mes = self.client.client.send_message('#unregister ' + self.username)
            if err == False:
                self.onError(mes)
                return
        if self.client.server:
            self.client.server.stop_server()

        event.accept()

    """
        handlers registered for external gui usage
        signal the gui thread
    """
    def display_user(self, user):
        if user == None:
            user = self.username

        self.emit(QtCore.SIGNAL('onAddUser(QString)'), user)

    def remove_user(self, user):
        self.emit(QtCore.SIGNAL('onUserExit(QString)'), user)

    def remove_all(self):
        self.emit(QtCore.SIGNAL('onServerExit()'))

    def display_line(self, user, line, color):
        self.emit(QtCore.SIGNAL('onNewMessage(QString,QString,QString)'), user, line, color)

    def display_success(self):
        self.emit(QtCore.SIGNAL('onOkRegister()'))

    def display_modify(self):
        self.emit(QtCore.SIGNAL('onModify()'))

    def displayErr(self, mes):
        self.emit(QtCore.SIGNAL('onErr(QString)'), mes)

    def displayWarn(self, mes):
        self.emit(QtCore.SIGNAL('onWarn(QString)'), mes)

    def displayInfo(self, mes):
        self.emit(QtCore.SIGNAL('onInfo(QString)'), mes)

    def displayDbg(self, mes):
        self.emit(QtCore.SIGNAL('onDbg(QString)'), mes)

    def displayBug(self, mes):
        self.emit(QtCore.SIGNAL('onBug(QString)'), mes)


    """
    """

    """
        handlers that modify the guy on different events/signa;s
    """
    def onSendClicked(self):
        self.parse_text()

    def onUpArrow(self):
        if len(self.command_hist) == 0:
            return

        self.holder.getSendWindow().setText(self.command_hist[self.command_idx])
        if self.command_idx <= 0:
            self.command_idx = len(self.command_hist) - 1
        self.command_idx -= 1

    def onDownArrow(self):
        self.holder.getSendWindow().clear()

    def onSendEnterPressed(self, e):
        self.parse_text()

    def onAddUser(self, user):
        icon = QtGui.QIcon('online.ico')
        item = QtGui.QListWidgetItem(user)
        item.setIcon(icon)

        self.holder.addRow(item)

        if user != self.username:
            self.holder.writeLog("user <b>" + user + "</b> is now online", self.holder.LEVEL_INFO)

    def onNewMessage(self, user, line, color):
        colorstr = Helpers.fontWithGivenColor(color)

        printstr = colorstr + '<b>' + user + ':</b><\\font> ' + line
        self.holder.writeMessage(printstr)
        scores = self.analyzer.get_score_for_phrase(str(line))
        for s in self.analyzer.depeche_sents:
            if s in scores:
                self.holder.set_pbar_value(s, scores[s])
            else:
                self.holder.set_pbar_value(s, 0)



    def onOkRegister(self):
        self.holder.writeLog('registered with username <b>' + self.username + '<\b>', self.holder.LEVEL_INFO)

    def onModify(self):
        self.holder.writeLog('succesfully changed name to <b>' + self.username + '</b>', self.holder.LEVEL_INFO)

        for idx in xrange(self.holder.getStatusWindow().count()):
            item = self.holder.getStatusWindow().item(idx)
            if item.text() == self.olduser:
                item.setText(self.username)

    def onUserExit(self, user):
        for idx in xrange(self.holder.getStatusWindow().count()):
            item = self.holder.getStatusWindow().item(idx)
            if item.text() == user:
                self.holder.getStatusWindow().takeItem(idx)
                return

    def onServerExit(self):
        self.holder.getStatusWindow().clear()
        self.holder.writeLog("Server stopped", self.holder.LEVEL_INFO)

    def onError(self, mes):
        self.holder.writeLog(mes, self.holder.LEVEL_ERR)

    def onInfo(self, mes):
        self.holder.writeLog(mes, self.holder.LEVEL_INFO)

    def onWarn(self, mes):
        self.holder.writeLog(mes, self.holder.LEVEL_WARN)

    def onBug(self, mes):
        self.holder.writeLog(mes, self.holder.LEVEL_BUG)

    def onDbg(self, mes):
        self.holder.writeLog(mes, self.holder.LEVEL_DBG)
    """
    """



class SendLineEdit(QtGui.QLineEdit):
    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)

    def event(self, event):
        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Return):
            self.emit(QtCore.SIGNAL('returnPressed'))
            return True

        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Up):
            self.emit(QtCore.SIGNAL('upPressed'))
            return True

        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Down):
            self.emit(QtCore.SIGNAL('downPressed'))

        return QtGui.QLineEdit.event(self, event)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = SAChat()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
