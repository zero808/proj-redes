#!/usr/bin/env python3
import socket
import sys
import AuxiliaryFunctions

BUFFER_SIZE = 1024

class TCPServer:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((HOST,PORT)) 
            self.fullMessage = b''
        except socket.error as e:
            print('error creating socket:', e)
            sys.exit(1)

    def establishConnection(self):
        try:        
            self.sock.listen() # not specified, default value is 5
            self.connection, self.clientAddress = self.sock.accept() # returns new connection and the client address
        except socket.error as e:
            print('error connecting to the user:', e)

    def receiveMessage(self):
        try:
            
            data = self.connection.recv(BUFFER_SIZE)

            self.fullMessage = b''
            while True: # messages will end with \n
                self.fullMessage += data
                if data.endswith(b'\n'): # tries again to check if there's more to it
                    self.connection.settimeout(1)
                    data = self.connection.recv(BUFFER_SIZE)
                    self.fullMessage += data

                data = self.connection.recv(BUFFER_SIZE)

            return self.fullMessage

        except socket.timeout:
            return self.fullMessage

    def sendMessage(self, data):    
        try:                  
            self.connection.sendall(data)
        except socket.error as e:
            print('error on send:', e)
            sys.exit(1)

    def closeConnection(self):
        try:
            self.connection.close()
            self.sock.close()
        except socket.error as e:
            print('error on close:', e)
            sys.exit(1)
