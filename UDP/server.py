#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
import sys
import socket
import time

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
	
	@abstractmethod
	def interpretMessage(self, message):
		pass
	
	def sendReply(self, reply, addr):
		reply += b'\n'
		self.s.sendto(reply, addr)
		return reply			

	def run(self):
		
		# will have the final message to interpret
		receivedMessage = {}
		while True:
			# receive (part of) message from the socket
			try:
				data, addr = self.s.recvfrom(self.BUFFER_SIZE)
			except:
				try:
					self.sendReply(str.encode("ERR"), addr)
				except:
					print("Cannot reach " + str(addr))
				finally:
					break
			
			str_addr = str(addr)
			if str_addr in receivedMessage.keys():
				receivedMessage[str_addr] += data
			else:
				receivedMessage[str_addr] = data
			
			# if data has \n, it means that is necessary interpret the message
			if b'\n' in data:
				#print('From', addr, 'is', receivedMessage[str_addr])
				receivedMessage[str_addr] = receivedMessage[str_addr].decode('UTF-8')
				# to verify if data received ends with \n
				dataArray = receivedMessage[str_addr].split("\n")
				if len(dataArray) != 2 or dataArray[1] != '':
					self.sendReply(str.encode('ERR'), addr)
					break
				
				# to verify if data has more than one space between words
				if "" in receivedMessage[str_addr].split(" "):
					self.sendReply(str.encode('ERR'), addr)
					break
					
				try:
					reply = str.encode(self.interpretMessage(receivedMessage[str_addr]))
				except IOError as msg:
					reply = str.encode(str(msg))
				except Exception:
					reply = str.encode("ERR")
				
				try:
					reply = self.sendReply(reply, addr)
					#print('Sent to', addr, "is", reply)
					if reply == str.encode("ERR"):
						break
				except:
					print("Cannot reach " + str(addr))
					break
				
				receivedMessage[str_addr] = b''
		
		self.s.close()
	
