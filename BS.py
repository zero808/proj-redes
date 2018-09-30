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

userList = {} 

# Main Functions

# Confirmation of the user registration
def handleUserRegistry(status):
    fullResponse = AuxiliaryFunctions.encode('LUR ' + status + '\n')
    server.sendMessage(csName, fullResponse, csPort)

# Adds a new user to the userList
def registerUser(userData):
    if len(userData) != 2 or not isinstance(userData[0], int):
        handleUserRegistry('ERR')
        raise IOError("syntax error")
    
    userName = userData[0]
    userPassword = userData[1]
    userList[userName] = userPassword

    if userName in userList and userList.get(userName) == userPassword:
        # if userList was updated correctly
        handleUserRegistry('OK')
        print('user registered')
    else:
        # if userList was not updated correctly
        handleUserRegistry('NOK')

    waitForMessage()

# Handles the deregistry of the BS
def deregister():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('UNR' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    server.sendMessage(csName, fullRequest, csPort)
    
    waitForMessage()


# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    server.sendMessage(csName, fullRequest, csPort)

    waitForMessage()

# Handles the registry response from the CS
def handleRegistryResponse(confirmation):
    if confirmation[0] == 'OK':
        print('registry successfull')
    elif confirmation[0] == 'NOK':
        print('registry not successfull')
    else:
        print('syntax error')

# Handles the deregistry response from the CS
def handleDeregistryResponse(confirmation):
    if confirmation[0] == 'OK':
        print('deregistry successfull')
    elif confirmation[0] == 'NOK':
        print('deregistry not successfull')
    else:
        print('syntax error')
        

# Ensures that the BS is 'always on' and receives the CS and user requests and responses
def waitForMessage():
    # all possible messages
    allRequests = {
        'RGR': handleRegistryResponse,
        'UAR': handleDeregistryResponse,
        'LSU': registerUser
    }

    # waits for a request
    message, address = server.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()

    func = allRequests.get(confirmation[0])

    if func == None:
        raise IOError('ERR')
    else:
        return func(confirmation[1:])
    

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
    try:
        global server 
        global bsTCPPort
        global csName
        global csPort

        bsTCPPort, csName, csPort = getArguments(argv)
        server = UDPserver.UDPServer(bsName, bsUDPPort)
        register()
        waitForMessage()
    except KeyboardInterrupt:
        deregister()
        print('BS service deregistered')
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])