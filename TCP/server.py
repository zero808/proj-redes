from abc import ABCMeta, abstractmethod
import sys
import os
import socket

class TCPServer(metaclass=ABCMeta):
	
	def __init__(self, TCP_IP, TCP_PORT):
		self.TCP_PORT = TCP_PORT
		self.TCP_IP = TCP_IP
		self.BUFFER_SIZE = 4096
		self.currentUser = None
		self.currentPassword = None
		
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.bind((self.TCP_IP, self.TCP_PORT))
			self.s.listen()
		except socket.gaierror as msg:
			raise IOError('Bind was not successful')
		except socket.error as msg:
			raise IOError('Something went wrong in the process of socket creation')

	def run(self):		
		while True:
			conn, addr = self.s.accept()
			
			pidChild = os.fork()
			if pidChild == 0:
				self.newConnection(conn, addr)
				os._exit(0)
			elif pidChild == -1:
				# will try again
				pidChild = os.fork()
				if pidChild == 0:
					self.newConnection(conn, addr)
					os._exit(0)
	
	@abstractmethod
	def interpretMessage(self, message):
		pass
	
	def sigalrm_handler(_signo, _stack_frame):
		if self.addr:
			self.sendReply(str.encode("ERR"), self.addr)
	
	def sendReply(self, conn, reply):
		reply += b'\n'
		conn.send(reply)
		return reply
	
	def newConnection(self, conn, addr):
		print('Connection address:', addr)
		
		# will have the final message to interpret
		receivedMessage = b''
		while True:
			# receive (part of) message from the socket
			data = b''
			try:
				data = conn.recv(self.BUFFER_SIZE)
			except:
				try:
					self.sendReply(conn, str.encode("ERR"))
				except:
					print("Cannot reach " + str(addr))
				finally:
					break
			
			receivedMessage += data
			
			if receivedMessage == b'':
				print("Close connection with", addr)
				break
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				print('From', addr, 'is', receivedMessage)
				receivedMessage = receivedMessage.decode('UTF-8')
				# to verify if data received ends with \n
				dataArray = receivedMessage.split("\n")
				if len(dataArray) != 2 or dataArray[1] != '':
					self.sendReply(conn, str.encode('ERR'))
					break
				
				# to verify if data has more than one space between words
				if "" in receivedMessage.split(" "):
					self.sendReply(conn, str.encode('ERR'))
					break
				
				if receivedMessage[:3] == "AUT" and self.currentUser is not None:
					self.sendReply(conn, str.encode('ERR'))
					break					
				
				try:
					reply = str.encode(self.interpretMessage(receivedMessage))				
				except IOError as msg:
					reply = str.encode(str(msg))
				except Exception as msg:
					reply = str.encode("ERR")
				
				try:
					reply = self.sendReply(conn, reply)
					print('Sent to', addr, "is", reply)
					if reply == str.encode("ERR"):
						break
				except:
					print("Cannot reach " + str(addr))
					break
				
				receivedMessage = b''
		
		conn.close()