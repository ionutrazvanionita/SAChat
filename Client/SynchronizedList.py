"""
 Python List with Synchronized access
"""

from threading import Lock

class SList:
	def __init__(self):
		self.list = []
		self.lock = Lock()

	def add(self, el):
		self.lock.acquire()
		self.list.append(el)
		self.lock.release()

	def remove(self, el):
		self.lock.acquire()
		self.list.remove(el)
		self.lock.release()

	def lock_list(self):
		self.lock.acquire()

	def unlock_list(self):
		self.lock.release()

	def get_list(self):
		return self.list


