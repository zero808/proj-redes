#!/usr/bin/env python3
import socket
import sys
import argparse
import os
import shutil
import datetime
import signal
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsName = socket.gethostbyname(socket.gethostname())
bsUDPPort = 9997

parentPid = os.getpid() #parent process id

userList = {} 

# SIGNAL HANDLERS

# Process kill
def handleProcessKill(sig, frame):
    if os.getpid() == parentPid:
        endConnection()
        sys.exit(1)
    else:
        deregister()
        sys.exit(1)

# Ctrl + c - deregisters the bs and closes the connections
def handleKeyboardInterruption(sig, frame):
    if os.getpid() == parentPid:
        #endConnection()
        sys.exit(1)
    else:
        deregister()
        sys.exit(1)


# MAIN FUNCTIONS

###################
#    User - BS   #
# (TCP Protocol) #
##################

# Closes the TCP connection
def endConnection():
    tcpserver.closeConnection()

def newConnection():
    tcpserver = TCPserver.TCPServer(bsName, bsTCPPort)
    tcpserver.establishConnection()

# Sends the dirName files to the user
def restoreDir(dirName):
    try:
        fileListString = b''
        auxiliaryString = ''
        encodedAuxiliaryString = b''
        nFiles = 0
        with os.scandir(dirName) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    nFiles += 1
                    auxiliaryString = auxiliaryString + ' ' + str(entry.name) + ' '
                    fileStats = os.stat(dirName+'/'+entry.name)

                    fileSeconds = fileStats.st_mtime
                    fileDateTime = AuxiliaryFunctions.stringTime(fileSeconds)
                    auxiliaryString += fileDateTime
                    fileSize = fileStats.st_size
                    auxiliaryString = auxiliaryString + str(fileSize) + ' '
                    encodedAuxiliaryString = AuxiliaryFunctions.encode(auxiliaryString)

                    with open(str(dirName + '/' + entry.name), "rb") as binary_file:
                        # Read the whole file at once
                        data = binary_file.read()
                        encodedAuxiliaryString += data
                    
                    fileListString += encodedAuxiliaryString
                    auxiliaryString = ''
                    encodedAuxiliaryString = b''

        fileListString = AuxiliaryFunctions.encode('RBR ' + str(nFiles)) + fileListString + AuxiliaryFunctions.encode('\n')
        tcpserver.sendMessage(fileListString)
        #endConnection() 
        #newConnection()
                    
    except OSError as e:
        fullResponse = AuxiliaryFunctions.encode('RBR ERR\n')
        tcpserver.sendMessage(fullResponse)
        #endConnection()
        sys.exit(1) 
    
# Receives the files from the user
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

                fileDateString = str(fileData[argCount + 1])
                fileDate = AuxiliaryFunctions.dateEpoch(fileDateString)
                
                fileTimeString = str(fileData[argCount + 2])
                fileTime = AuxiliaryFunctions.timeEpoch(fileTimeString)
                
                fileSize = int(fileData[argCount + 3])
                data = AuxiliaryFunctions.encode(fileData[argCount + 4])
                
                backupFile = open(fileName, 'wb') # gonna write bytes
                backupFile.write(data)
                
                os.utime(fileName, (fileDate + fileTime, fileDate + fileTime))
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

# User authentication
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

# Handles the restore Directory request
def handleRestoreDirRequest(directory): 
    try:
        dirName = str(directory[0])
        print(dirName)
        if len(directory) != 1:
            fullResponse = AuxiliaryFunctions.encode('RBR ERR\n')
            tcpserver.sendMessage(fullResponse)
        else:
            # calls the function responsible for sending the dirName files to the user
            restoreDir(dirName)
    except ValueError:
        fullResponse = AuxiliaryFunctions.encode('RBR ERR\n')
        tcpserver.sendMessage(fullResponse)
        print('Value Error')

# Confirmation of the file backup
def handleFileBackup(status):
    fullResponse = AuxiliaryFunctions.encode('UPR ' + status + '\n')
    tcpserver.sendMessage(fullResponse)
    #endConnection()
    #newConnection()

# Confirmation of the user authentication
def handleUserAuthentication(status):
    fullResponse = AuxiliaryFunctions.encode('AUR ' + status + '\n')
    print('vai enviar mensagem')
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

    func = allRequests.get(confirmation[0])

    if func == None:
        handleUnexpectedTCPProtocolMessage()
    else:
        func(confirmation[1:])



##################
#     CS - BS    #
# (UDP Protocol) #
##################

# Sends the list of files in dirName to the CS
def sendFileList(dirName, csAddress):
    try:
        newCSname = str(csAddress[0])
        newCSport = int(csAddress[1])
        fileListString = ''
        nFiles = 0
        with os.scandir(dirName) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file(): 
                    nFiles += 1

                    fileListString = fileListString + ' ' + str(entry.name) + ' '

                    fileStats = os.stat(dirName+'/'+entry.name)

                    fileSeconds = fileStats.st_mtime
                    fileDateTime = AuxiliaryFunctions.stringTime(fileSeconds)
                    fileListString += fileDateTime

                    fileSize = fileStats.st_size
                    fileListString = fileListString + str(fileSize)

        fullFileString = 'LFD ' + str(nFiles) + fileListString + '\n'
        encodedFileString = AuxiliaryFunctions.encode(fullFileString)
        udpserver.sendMessage(newCSName, fullResponse, newCSport)
    except ValueError:
        print('syntax error')
    except OSError as e:
        print(e)
        sys.exit(1)

# Deletes a directory from an user
def deleteDirectory(dirData, csAddress):
    try:
        userName = int(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            handleDirDeletion('NOK', csAddress)
        elif userName not in userList:
            handleDirDeletion('NOK', csAddress)
        else:
            shutil.rmtree(dirName)
            handleDirDeletion('OK', csAddress)

    except ValueError:
        handleDirDeletion('NOK', csAddress)
    except OSError as e:
        handleDirDeletion('NOK', csAddress)
        sys.exit(1)

# Adds a new user to the userList
def registerUser(userData, csAddress):
    try:
        print('entrou no register user')
        userName = int(userData[0])
        userPassword = str(userData[1])
        if len(userData) != 2:
            # syntax error
            handleUserRegistry('ERR', csAddress)
        elif userName in userList and userList.get(userName) == userPassword:
            # if the userList was not updated
            handleUserRegistry('NOK', csAddress)
        else:
            print('vai criar um user novo:', userName, userPassword)
            userList[userName] = userPassword
            # if userList was updated correctly
            handleUserRegistry('OK', csAddress)
            print('New user: ', userName)

    except ValueError:
        handleUserRegistry('ERR')

# Handles the deregistry of the BS
def deregister():
    print('entrou do deregister')
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('UNR' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)
    print('mensagem enviada')
    waitForCSMessage()
    print('recebeu confirmação')
    udpserver.closeConnection() 
    print('ligação terminada')

# Handles the registry of the new BS 
def register():
    print('entrou no register')
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)
    print('mensagem enviada:')
    print(fullRequest)

# Handles the CS request to list the files in a dir
def handleListFilesRequest(dirData, csAddress):
    try:
        userName = int(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            print('syntax error')
        elif userName not in userList:
            # if the user doesn't exist or the password is wrong
            print('user error')
        else:
            # calls the function responsible for sending the file list
            sendFileList(dirName, csAddress)
        
    except ValueError:
        print('syntax error')

# Confirmation of the user directory deletion
def handleDirDeletion(status, csAddress):
    newCSname = str(csAddress[0])
    newCSport = int(csAddress[1])
    fullResponse = AuxiliaryFunctions.encode('DBR ' + status + '\n')
    udpserver.sendMessage(newCSName, fullResponse, newCSport)
    #udpserver.sendMessage('192.168.1.65', fullResponse, 9995)

# Handles the registry response from the CS
def handleRegistryResponse(confirmation, csAddress):
    print('entrou no handleRegistryResponse')
    print('confirmation:', confirmation)
    if confirmation[0] == 'OK':
        print('registry successfull')
    elif confirmation[0] == 'NOK':
        print('registry not successfull')
    else:
        print('syntax error')

# Handles the deregistry response from the CS
def handleDeregistryResponse(confirmation, csAddress):
    if confirmation[0] == 'OK':
        print('deregistry successfull')
    elif confirmation[0] == 'NOK':
        print('deregistry not successfull')
    else:
        print('syntax error')

# Confirmation of the user registration
def handleUserRegistry(status, csAddress):
    print('entrou no handleUserRegistry:', status, csAddress)
    newCSname = str(csAddress[0])
    newCSport = int(csAddress[1])
    print(newCSname, newCSport)
    fullResponse = AuxiliaryFunctions.encode('LUR ' + status + '\n')
    print(fullResponse)
    udpserver.sendMessage(newCSname, fullResponse, newCSport)    
    print('enviou a mensagem ao CS')

# Handles unexpected UDP protocol messages
def handleUnexpectedUDPProtocolMessage():
    print('entrou no handleUnexpectedUDPProtocol')
    fullResponse = AuxiliaryFunctions.encode('ERR\n')
    udpserver.sendMessage(csName, fullResponse, csPort)

# Receives the CS requests and responses
def waitForCSMessage():
    print('waiting for message')
    # waits for a request
    message, address = udpserver.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()

    func = allRequests.get(confirmation[0])
    if func == None:
        handleUnexpectedUDPProtocolMessage()
    else:
        print('vai entrar na função:')
        print(func)
        func(confirmation[1:], address)



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

    print(csName, csPort)
    return (int(bsTCPPort), csName, int(csPort))

def main(argv):
    global bsTCPPort, csName, csPort, newCSname, newCSport
    global allRequests
    global pidUDPserver
    global udpserver, tcpserver

    allRequests = {
        'RGR': handleRegistryResponse,
        'UAR': handleDeregistryResponse,
        'LSU': registerUser,
        'AUT': authenticateUser,
        'UPL': uploadFile,
        'DLB': deleteDirectory,
        'LSF': handleListFilesRequest,
        'RSB': handleRestoreDirRequest
    }

    bsTCPPort, csName, csPort = getArguments(argv)
    newCSname = csName
    newCSport = csPort
    bsUDPPort = bsTCPPort

    try: 
        pidUDPserver = os.fork()
    except OSError as e:
        print('Could not create a child process')
        sys.exit(1)
    
    if pidUDPserver == 0:
        # child process (UDP)
        udpserver = UDPserver.UDPServer(bsName, bsUDPPort)
        register()

        while True:
            waitForCSMessage()
        
    
    else:
        # parent process (TCP)
        tcpserver = TCPserver.TCPServer(bsName, bsTCPPort)
        tcpserver.establishConnection()
        
        while True:
            waitForUserMessage()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handleKeyboardInterruption)
    signal.signal(signal.SIGTERM, handleProcessKill)
    main(sys.argv[1:])
    sys.exit(0)