#!/usr/bin/env python3
import socket
import sys
import argparse
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsName = socket.gethostname()

REG = 'REG'


# Main Functions


# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode(REG + ' ' + bsName + ' ' + str(bsPort))
    server.sendMessage(csName, fullRequest, csPort)



# Reads the arguments from the command line
def getArguments(argv):
    parser = argparse.ArgumentParser(argv)
    parser.add_argument('-b', help = 'Backup Server port', default = '59000')
    parser.add_argument('-n', help = 'Central Server name', default = 'localhost')
    parser.add_argument('-p', help = 'Central Server port', default = '58004')
    args = parser.parse_args()

    d = vars(args)
    bsPort = d['b']
    csName = d['n']
    csPort = d['p']

    # print(bsPort, csName, csPort)
    return (int(bsPort), csName, int(csPort))

def main(argv):
    global server 
    global bsPort
    global csName
    global csPort

    bsPort, csName, csPort = getArguments(argv)
    #print(bsPort, csName, csPort)
    server = UDPserver.UDPServer(bsName, bsPort)
    register()

if __name__ == "__main__":
    main(sys.argv[1:])