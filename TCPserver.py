#!/usr/bin/env python3
import socket
import sys

BUFFER_SIZE = 4096

class TCPServer:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST,PORT))

    def establishConnection(self):
        self.sock.listen() # not specified, default value is 5
        self.connection, self.clientAddress = self.sock.accept() # returns new connection and the client address
        print('Connected by ', self.clientAddress)

    def handle(self):
        while True:
            data = self.connection.recv(BUFFER_SIZE)
            if not data: break
                #if data.endswith(b'\n'): messages will end with \n
                #    break
            self.connection.sendall(data)

    def closeConnection(self):
        self.sock.close()
        self.connection.close()


# Global Variables
#
#HOST = 'localhost'
#PORT = 9999
#BUFFER_SIZE = 4096

#if __name__ == "__main__":
#    server = TCPServer(HOST, PORT)
#    server.establishConnection()
#    server.handle()
#    server.closeConnection()


#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((HOST,PORT))
#s.listen() # not specified, default value is 5
#connection, clientAddress = s.accept() # returns new connection and the client address
#print('Connected by ', clientAddress)
#while True:
#    data = connection.recv(BUFFER_SIZE)
#    if not data: break
#    #if data.endswith(b'\n'): messages will end with \n
    #    break
#    connection.sendall(data)

#connection.close()