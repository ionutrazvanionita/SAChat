__author__ = 'ionut'

from PyQt4 import QtGui, QtCore
from random import randint


helpInfo = "Type #help for list of available commands"
helpMessage = """#help
    #register <user> <remote_host> <remote_port> - connect to chat server")
    #clear - clears message history")
    #listen <host> <port> - set ip and andress where to receive messages")
    #logout - logs out from the current server
    """

listenInfo = "<b>IMPORTANT: </b>Before connecting to a server you must set your listening interface with #listen"

def printMessage(widget, message):
    widget.append(message)

def printHelpInfo(widget):
    printMessage(widget, helpInfo)

def printHelpMessage(widget):
    printMessage(widget, helpMessage)

def printListenInfo(widget):
    printMessage(widget, listenInfo)

def genSixDigitHex():

    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    if r < 16:
        pad='0'
    elif r == 0:
        pad='00'
    else:
        pad=''

    color = 0
    color = (r<<16) + (g<<8) + b
    return pad + str(hex(color)[2:])

def fontWithRandColor():
    return fontWithGivenColor(genSixDigitHex())

def fontWithGivenColor(color):
    return "<font color=\"#" + color + "\">"


class WidgetHolder:
    DBG = "<b>DEBUG: </b>"
    INFO = "<b>INFO: </b>"
    WARN = "<b>WARNING: </b>"
    ERR = "<b>ERROR: </b>"
    BUG = "<b>BUG: </b>"

    LEVEL_DBG  = 4
    LEVEL_INFO = 3
    LEVEL_WARN = 2
    LEVEL_ERR  = 1
    LEVEL_BUG  = 0


    def __init__(self):
        self.chatWindow   = None
        self.sendButton   = None
        self.sendWindow   = None
        self.statusWindow = None
        self.pbar_dict    = {}

    def setChatWindow(self, window):
        self.chatWindow = window

    def getChatWindow(self):
        return self.chatWindow

    def setSendButton(self, button):
        self.sendButton = button

    def getSendButton(self):
        return self.sendButton

    def setSendWindow(self, window):
        self.sendWindow = window

    def getSendWindow(self):
        return  self.sendWindow

    def setStatusWindow(self, window):
        self.statusWindow = window

    def getStatusWindow(self):
        return self.statusWindow

    """
        send window related functions
    """
    def getWrittenMessage(self):
        return str(self.sendWindow.displayText())

    def getWrittenMessageAndClear(self):
        ret = str(self.sendWindow.displayText())
        self.sendWindow.clear()
        return ret
    """
    """

    """
        chat window related functions
    """
    def clearChatWindow(self):
        self.chatWindow.clear()


    def writeLog(self, mes, level):
        if level == self.LEVEL_BUG:
            self.chatWindow.append(self.BUG + mes)
        elif level == self.LEVEL_ERR:
            self.chatWindow.append(self.ERR + mes)
        elif level == self.LEVEL_WARN:
            self.chatWindow.append(self.WARN + mes)
        elif level == self.LEVEL_INFO:
            self.chatWindow.append(self.INFO + mes)
        elif level == self.LEVEL_DBG:
            self.chatWindow.append(self.DBG + mes)

    def writeMessage(self, mes):
        self.chatWindow.append(mes)

    def writeColoured(self, mess, colour):
        colstr = fontWithGivenColor()
        colstr += mess
        self.writeMessage(colstr)

    """
    """

    """
        status window related functions
    """
    def clearStatusWindow(self):
        self.statusWindow.clear()

    def addRow(self, item):
        self.statusWindow.addItem(item)
    """
    """

    """
        progress bar related functions
        each progress bar is held inside a dictionary
        each key of the dictionary represents a sentiment
    """
    def set_pbar(self, sent, pbar):
        self.pbar_dict[sent] = pbar

    def get_pbar(self, sent):
        return self.pbar_dict[sent]

    def set_pbar_value(self, sent, value):
        self.pbar_dict[sent].setValue(int(value*100))




