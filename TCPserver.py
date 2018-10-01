#!/usr/bin/env python3
import socket
import sys
import AuxiliaryFunctions

BUFFER_SIZE = 4096

class TCPServer:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((HOST,PORT))
        except socket.error as e:
            print('error creating socket', e)
            sys.exit(1)

    def establishConnection(self):
        try:        
            self.sock.listen() # not specified, default value is 5
            self.connection, self.clientAddress = self.sock.accept() # returns new connection and the client address
            print('Connected by ', self.clientAddress)
        except socket.error as e:
            print('error connecting to the user: ', e)

    def receiveMessage(self):
        try:
            data = self.connection.recv(BUFFER_SIZE)

            print(data)

            if not data: return None

            fullMessage = b''
            while True: # messages will end with \n
                fullMessage += data
                print('fullMessage: ', fullMessage)
                if b'\n' in data:
                    break

                data = self.connection.recv(BUFFER_SIZE)

            #print('chegou aqui')
            return fullMessage

        except socket.error as e:
            print('error on recv: ', e)
            sys.exit(1)

    def sendMessage(self, data):    
        try:                  
            self.connection.sendall(data)
        except socket.error as e:
            print('error on send: ', e)
            sys.exit(1)

    def closeConnection(self):
        self.connection.close()
        self.sock.close()


# Global Variables
#
#HOST = 'localhost'
#PORT = 9999
#BUFFER_SIZE = 4096

#if __name__ == "__main__":


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