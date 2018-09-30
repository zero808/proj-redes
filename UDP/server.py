from abc import ABCMeta, abstractmethod
import sys
import socket

class UDPServer(metaclass=ABCMeta):

	def __init__(self, UDP_IP, UDP_PORT):
		self.UDP_PORT = UDP_PORT
		self.UDP_IP = UDP_IP
		self.BUFFER_SIZE = 4096
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.s.bind((self.UDP_IP, self.UDP_PORT))
		except socket.error as msg:
			raise IOError('Something went wrong in the process of socket creation')
			

	def run(self):
		
		# will have the final message to interpret
		receivedMessage = {}
		while True:
			# receive (part of) message from the socket
			try:
				data, addr = self.s.recvfrom(self.BUFFER_SIZE)
			except:
				raise IOError('recvfrom failed')
			
			str_addr = str(addr)
			if (str_addr in receivedMessage.keys()):
				receivedMessage[str_addr] += data
			else:
				receivedMessage[str_addr] = data
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				print('From', addr, 'is', receivedMessage[str_addr])
				try:
					reply = str.encode(self.interpretMessage(receivedMessage[str_addr]))				
				except IOError as msg:
					raise IOError(msg)
				except:
					raise IOError('ERR')
				
				receivedMessage[str_addr] = b''
				reply += b'\n'
				self.s.sendto(reply, addr)
				print('Sent to', addr, "is '", reply, "'")
		
		self.s.close()
	
	@abstractmethod
	def interpretMessage(self, message):
		pass
