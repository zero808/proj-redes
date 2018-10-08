#!/usr/bin/env python3
import socket
import sys
import argparse
import os
import shutil
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsName = socket.gethostbyname(socket.gethostname())
bsUDPPort = 9997

userList = {} 

# Main Functions

#############
# User - BS #
#############

# receives the files from the user
def uploadFile(fileData):
    try:
        directoryName = str(fileData[0])
        numberOfFiles = int(fileData[1])

        if len(fileData) != (numberOfFiles * 5 + 2):
            handleFileBackup('NOK')
        
        else:
            os.mkdir(directoryName)
            print(directoryName,':', end=' ')
            argCount = 2
            for i in range(0, numberOfFiles):
                fileName = str(fileData[argCount])
                fileDate = str(fileData[argCount + 1])
                fileTime = str(fileData[argCount + 2])
                fileSize = int(fileData[argCount + 3])
                data = fileData[argCount + 4]

                backupFile = open(fileName, 'w')
                backupFile.write(data)
                shutil.move(fileName, directoryName) 

                print(fileName, fileSize, 'Bytes received', end='\n')
                argCount += 5

            handleFileBackup('OK')
    except ValueError:
        handleFileBackup('NOK')
    except OSError as e:
        handleFileBackup('NOK')
        print('Error handling files or directories', e)
        sys.exit(1)

# user authentication
def authenticateUser(userData):
    try:
        userName = int(userData[0])
        userPassword = userData[1]
        if len(userData) != 2:
            handleUserAuthentication('NOK')
        elif userName not in userList or (userName in userList and userList.get(userName) != userPassword):
            # if the user doesn't exist or the password is wrong
            handleUserAuthentication('NOK')
        else:
            # valid authentication
            handleUserAuthentication('OK')

    except ValueError:
        # if the userName isn't an int
        handleUserAuthentication('NOK')

def handleFileBackup(status):
    fullResponse = AuxiliaryFunctions.encode('UPR ' + status + '\n')
    tcpserver.sendMessage(fullResponse)

# confirmation of the user authentication
def handleUserAuthentication(status):
    fullResponse = AuxiliaryFunctions.encode('AUR ' + status + '\n')
    tcpserver.sendMessage(fullResponse)

# Handles unexpected TCP protocol messages
def handleUnexpectedTCPProtocolMessage():
    fullResponse = AuxiliaryFunctions.encode('ERR\n')
    tcpserver.sendMessage(fullResponse)

# Receives the user requests and responses
def waitForUserMessage():

    # waits for a request/response
    message = tcpserver.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()

    print(confirmation)

    func = allRequests.get(confirmation[0])

    print(func)
    if func == None:
        print('ups')
        handleUnexpectedTCPProtocolMessage()
    else:
        print('entrou aqui')
        print('argumentos: ', confirmation[1:])
        return func(confirmation[1:])



#############
#  CS - BS  #
#############

# Adds a new user to the userList
def registerUser(userData):
    try:
        userName = int(userData[0])
        userPassword = userData[1]

        if len(userData) != 2:
            handleUserRegistry('ERR')
            # raise IOError("syntax error")
        elif userName in userList and userList.get(userName) == userPassword:
            # if the userList was not updated
            handleUserRegistry('NOK')
            print('list not updated')
        else:
            userList[userName] = userPassword
            # if userList was updated correctly
            handleUserRegistry('OK')
            print('New user: ', userName)

    except ValueError:
        handleUserRegistry('ERR')

# Handles the deregistry of the BS
def deregister():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('UNR' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)
    udpserver.closeConnection() 
    waitForCSMessage()

# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)
    print('registou')
    # waitForCSMessage()

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

# Confirmation of the user registration
def handleUserRegistry(status):
    fullResponse = AuxiliaryFunctions.encode('LUR ' + status + '\n')
    udpserver.sendMessage(csName, fullResponse, csPort)    

# Handles unexpected UDP protocol messages
def handleUnexpectedUDPProtocolMessage():
    fullResponse = AuxiliaryFunctions.encode('ERR\n')
    udpserver.sendMessage(csName, fullResponse, csPort)

# Receives the CS requests and responses
def waitForCSMessage():

    # waits for a request
    message, address = udpserver.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()

    func = allRequests.get(confirmation[0])

    if func == None:
        handleUnexpectedUDPProtocolMessage()
    else:
        return func(confirmation[1:])

# Reads the arguments from the command line
def getArguments(argv):
    parser = argparse.ArgumentParser(argv)
    parser.add_argument('-b', help = 'Backup Server port', default = '5005')
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
        global udpserver 
        global tcpserver
        global bsTCPPort
        global csName
        global csPort
        global allRequests

        allRequests = {
            'RGR': handleRegistryResponse,
            'UAR': handleDeregistryResponse,
            'LSU': registerUser,
            'AUT': authenticateUser,
            'UPL': uploadFile
        }

        bsTCPPort, csName, csPort = getArguments(argv)

        try: 
            pidTCPserver = os.fork()
        except OSError as e:
            print('Could not create a child process')
            sys.exit(1)
        
        if pidTCPserver == 0:
            print(bsName, bsTCPPort)
            tcpserver = TCPserver.TCPServer(bsName, bsTCPPort)
            tcpserver.establishConnection()

            while True:
                waitForUserMessage()
            
            tcpserver.closeConnection()
        
        else:
            udpserver = UDPserver.UDPServer(bsName, bsUDPPort)
            register()
            
            while True:
                waitForCSMessage()
            
            udpserver.closeConnection()
        
        try:
            pid, status = os.waitpid(pidTCPserver, 0)
        except OSError as e:
            print('Child process did not complete successfully')
            sys.exit(1)

    except KeyboardInterrupt:
        deregister()
        print('BS service deregistered')


if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)