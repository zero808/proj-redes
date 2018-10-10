from abc import ABCMeta, abstractmethod
import sys
import os
import socket

class UDPClient(metaclass=ABCMeta):
	
	def __init__(self, UDP_IP, UDP_PORT):
		self.UDP_PORT = UDP_PORT
		self.UDP_IP = UDP_IP
		self.BUFFER_SIZE = 4096
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.s.settimeout(5)
		except socket.error as msg:
			print('Something went wrong in the process of socket creation')
			sys.exit(1)
	
	# return the reply from the server
	def sendMessage(self, message):
		message = str.encode(message)
		message += b'\n'
		#print('Sent to', (self.UDP_IP, self.UDP_PORT), "is", message)
		self.s.sendto(message, (self.UDP_IP, self.UDP_PORT))
		
		receivedMessage = b""
		while True:
			# receive (part of) message from the socket
			try:
				i = 0
				while i < 3:
					data, addr = self.s.recvfrom(self.BUFFER_SIZE)
					i += 1
				if i == 3:
					raise IOError("Cannot receive the answer to the message " + str(message))
			except Exception as msg:
				print(str(msg))
				os._exit(1)
			receivedMessage += data
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				#print('From', addr, 'is', receivedMessage)
				
				receivedMessage = receivedMessage.decode('UTF-8')
				# to verify if data received ends with \n
				dataArray = receivedMessage.split("\n")
				if len(dataArray) != 2 or dataArray[1] != '':
					self.s.sendto(b'ERR', (self.UDP_IP, self.UDP_PORT))
					return "ERR"
				
				# to verify if data has more than one space between words
				if "" in receivedMessage.split(" "):
					self.s.sendto(b'ERR', (self.UDP_IP, self.UDP_PORT))
					return "ERR"
				
				return receivedMessage