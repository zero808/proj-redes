from abc import ABCMeta, abstractmethod
import sys
import socket

class UDPServer(metaclass=ABCMeta):

	def __init__(self, UDP_PORT):
		self.UDP_PORT = UDP_PORT
		self.UDP_IP = socket.gethostbyname(socket.gethostname())
		self.BUFFER_SIZE = 4096
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.s.bind((self.UDP_IP, self.UDP_PORT))
		except socket.error as msg:
			print('Something went wrong in the process of socket creation')
			sys.exit(1)

	def run(self):
		
		# will have the final message to interpret
		receivedMessage = []
		while True:
			# receive (part of) message from the socket
			try:
				data, addr = self.s.recvfrom(self.BUFFER_SIZE)
			except:
				print("recvfrom failed")
				sys.exit(1)
			receivedMessage[addr] += data
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				print('From', addr, 'is', receivedMessage)
				try:
					reply = str.encode(self.interpretMessage(receivedMessage))				
				except IOError as msg:
					print(msg)
					sys.exit(1)
				
				receivedMessage[addr] = b''
				self.s.sendto(reply + b'\n', addr)
				print('Sent to', addr, "is '", reply, "'")
		
		self.s.close()
	
	@abstractmethod
	def interpretMessage(self, message):
		pass
