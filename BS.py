#!/usr/bin/env python3
import socket
import sys
import argparse
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsName = socket.gethostbyname(socket.gethostname())
bsUDPPort = 9997

# Main Functions

# Handles the deregistry of the BS
def deregister():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('UNR' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    server.sendMessage(csName, fullRequest, csPort)

    # message, address = server.receiveMessage()
    message, address = server.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()
    
    if confirmation[0] == 'UAR':
        if confirmation[1] == 'OK':
            print('deregistry successfull')
        elif confirmation[1] == 'NOK':
            print('deregistry not successfull')
        else:
            print('syntax error')

# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    server.sendMessage(csName, fullRequest, csPort)

    # confirmation from CS
    message, address = server.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()
    
    if confirmation[0] == 'RGR':
        if confirmation[1] == 'OK':
            print('registry successfull')
        elif confirmation[1] == 'NOK':
            print('registry not successfull')
        else:
            print('syntax error')



# Reads the arguments from the command line
def getArguments(argv):
    parser = argparse.ArgumentParser(argv)
    parser.add_argument('-b', help = 'Backup Server port', default = '59000')
    parser.add_argument('-n', help = 'Central Server name', default = 'localhost')
    parser.add_argument('-p', help = 'Central Server port', default = '58004')
    args = parser.parse_args()

    d = vars(args)
    bsTCPPort = d['b']
    csName = d['n']
    csPort = d['p']

    return (int(bsTCPPort), csName, int(csPort))

def main(argv):
    global server 
    global bsTCPPort
    global csName
    global csPort

    bsTCPPort, csName, csPort = getArguments(argv)
    server = UDPserver.UDPServer(bsName, bsUDPPort)
    register()
    deregister()

if __name__ == "__main__":
    main(sys.argv[1:])