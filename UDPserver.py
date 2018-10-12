#!/usr/bin/env python3
import socket
import sys
import AuxiliaryFunctions

BUFFER_SIZE = 4096

class UDPServer:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((HOST,PORT))
        except socket.error as e:
            print('error creating socket: ', e)
            sys.exit(1)

    # Since there is no connection, the client address must be given explicitly
    # when sending data back via sendto()
    # request[0] is the data
    # request[1] is the client socket

    def receiveMessage(self):
        try:
            data, clientAddress = self.sock.recvfrom(BUFFER_SIZE)
            return (data, clientAddress)
        except socket.error as e:
            print('error on recv: ', e)
            sys.exit(1)

    def sendMessage(self, clientAddress, message, clientPort):
        try:
            self.sock.sendto(message, (clientAddress, clientPort))
        except socket.error as e:
            print('error on sendto: ', e)
            sys.exit(1)

    def closeConnection(self):
        self.sock.close()

