#!/usr/bin/env python3
import socket
import sys
import argparse
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsPort = 59000
bsName = socket.gethostname()
csName = 'localhost'
csPort = 58004

REG = 'REG'


# Main Functions


# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.writeRequest([REG,bsName,str(bsPort)])
    server.sendMessage(csName,fullRequest)



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

    return args

def main(argv):
    u = getArguments(argv)
    global server 
    server = UDPserver.UDPServer(bsName, bsPort)
    register()

if __name__ == "__main__":
    main(sys.argv[1:])