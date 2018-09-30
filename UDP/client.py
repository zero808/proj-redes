from abc import ABCMeta, abstractmethod
import sys
import socket

class UDPClient(metaclass=ABCMeta):
	
	def __init__(self, UDP_HOST, UDP_PORT):
		self.UDP_PORT = UDP_PORT
		self.UDP_IP = UDP_HOST
		self.BUFFER_SIZE = 4096
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as msg:
			print('Something went wrong in the process of socket creation')
			sys.exit(1)
	
	# return the reply from the server
	def sendMessage(self, message):
		message += b'\n'
		print('Sent to', (self.UDP_IP, self.UDP_PORT), "is '", reply, "'")
		self.s.sendto(message, (self.UDP_IP, self.UDP_PORT))
		
		while True:
			# receive (part of) message from the socket
			try:
				data, addr = self.s.recvfrom(self.BUFFER_SIZE)
			except:
				print("recvfrom failed")
				sys.exit(1)
			receivedMessage += data
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				print('From', addr, 'is', receivedMessage)
				return receivedMessage