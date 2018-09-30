from abc import ABCMeta, abstractmethod
import sys
import socket

class TCPServer(metaclass=ABCMeta):

	def __init__(self, TCP_PORT):
		self.TCP_PORT = TCP_PORT
		self.TCP_IP = socket.gethostbyname(socket.gethostname())
		self.BUFFER_SIZE = 4096
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.bind((self.TCP_IP, self.TCP_PORT))
			self.s.listen()
		except socket.gaierror as msg:
			print('Bind was not successful')
			sys.exit(1)
		except socket.error as msg:
			print('Something went wrong in the process of socket creation')
			sys.exit(1)
		

	def establishConnection(self):
		self.conn, self.addr = self.s.accept()

	def run(self):

		print('Connection address:', self.addr)
		
		# will have the final message to interpret
		receivedMessage = b''
		while True:
			# receive (part of) message from the socket
			try:
				data = self.conn.recv(self.BUFFER_SIZE)
			except:
				print("recv failed")
				sys.exit(1)
			
			receivedMessage += data
			
			if receivedMessage == b'':
				print("Close connection with", self.addr)
				break
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				print('From', self.addr, 'is', receivedMessage)
				
				try:
					reply = str.encode(self.interpretMessage(receivedMessage))				
				except IOError as msg:
					reply = msg
				except:
					print("ERR")
					sys.exit(1)
				
				receivedMessage = b''
				self.conn.send(reply + b'\n')
				print('Sent to', self.addr, "is '", reply, "'")
		
		self.conn.close()
	
	@abstractmethod
	def interpretMessage(self, message):
		pass
