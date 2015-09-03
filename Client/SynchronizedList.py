"""
 Python List with Synchronized access
"""

from threading import Lock

class SList:
    def __init__(self):
        self.list = []
        self.lock = Lock()

    def add(self, el):
        self.list.append(el)

    def remove(self, el):
        self.list.remove(el)

    def get_list(self):
        return self.list

    def get_lock(self):
        return self.lock


