#!/usr/bin/env python3
import socket
import sys
import AuxiliaryFunctions

BUFFER_SIZE = 4096

class UDPServer:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST,PORT))

    # Since there is no connection, the client address must be given explicitly
    # when sending data back via sendto()
    # request[0] is the data
    # request[1] is the client socket

    def receiveMessage(self):
        print('server is waiting for message')
        data, clientAddress = self.sock.recvfrom(BUFFER_SIZE)
        # print('Connected by ', clientAddress)
        # print('Received:', str(data, "utf-8"))
        return (data, clientAddress)

    def sendMessage(self, clientAddress, message, clientPort):
        self.sock.sendto(message, (clientAddress, clientPort))

    def closeConnection(self):
        self.sock.close()



# Global Variables
#
#HOST = 'localhost'
#PORT = 9999
#BUFFER_SIZE = 4096

#if __name__ == "__main__":
#    server = UDPServer(HOST, PORT)
#    data, clientAddress = server.receiveMessage()
#    print(data)
#    server.sendMessage(clientAddress[0], AuxiliaryFunctions.encode('RGR ERR'), clientAddress[1])
#    server.closeConnection()
