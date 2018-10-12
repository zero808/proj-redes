#!/usr/bin/env python3
import socket
import sys
import argparse
import os
import shutil
import datetime
import signal
from multiprocessing import Process, Value, Array
import UDPserver
import TCPserver
import AuxiliaryFunctions

# Global Variables

bsName = socket.gethostbyname(socket.gethostname())
bsUDPPort = 9997

parentPid = os.getpid() #parent process id


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
    print('esta na função upload file')
    try:
        print(fileData)
        directoryName = str(AuxiliaryFunctions.decode(fileData[0]))
        numberOfFiles = int(AuxiliaryFunctions.decode(fileData[1]))
        print('dir name:', directoryName, 'number of files:', numberOfFiles)
        print(len(fileData))
        print(numberOfFiles * 5 + 2)
        print(numberOfFiles)
        if len(fileData) != (numberOfFiles * 5 + 2):
            print('len errado')
            handleFileBackup('NOK')
        
        else:
            print('está no else')
            os.mkdir(directoryName)
            print(directoryName,':', end=' ')
            argCount = 2
            for i in range(0, numberOfFiles):
                fileName = str(AuxiliaryFunctions.decode(fileData[argCount]))

                fileDateString = str(AuxiliaryFunctions.decode(fileData[argCount + 1]))
                fileDate = AuxiliaryFunctions.dateEpoch(fileDateString)
                
                fileTimeString = str(AuxiliaryFunctions.decode(fileData[argCount + 2]))
                fileTime = AuxiliaryFunctions.timeEpoch(fileTimeString)
                
                fileSize = int(AuxiliaryFunctions.decode(fileData[argCount + 3]))
                #data = AuxiliaryFunctions.encode(fileData[argCount + 4])
                data = bytes(fileData[argCount + 4])
                
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
        userName = str(userData[0])
        userPassword = str(userData[1])
        if len(userData) != 2:
            print('len error')
            handleUserAuthentication('NOK')
            
        else:
            print('esta no else')
            authentic = False
            userFile = open('BSusers', 'r')  
            print('abriu o ficheiro')
            user = userFile.readline()
            print('leu a linha')
            while user:
                currentUserData = user.split(" ")
                if currentUserData[0] == userName:
                    print([currentUserData[1]])
                    print([userPassword.rstrip('\n')])
                    if currentUserData[1] == userPassword.rstrip('\n'):
                        print('a comparar passwords:', currentUserData[1], userPassword)
                        authentic = True
                        print('é autentico')
                        handleUserAuthentication('OK')
                user = userFile.readline()
            userFile.close()
                
            if not authentic:
                print('não é autentico')
                handleUserAuthentication('NOK')

    except ValueError:
        # if the userName isn't an int
        handleUserAuthentication('NOK')
    except OSError as e:
        print('Error handling the user list:',e)
        sys.exit(1)

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

# Confirmation of the user authentication
def handleUserAuthentication(status):
    print('status:',status)
    fullResponse = AuxiliaryFunctions.encode('AUR ' + status + '\n')
    print('vai enviar mensagem')
    tcpserver.sendMessage(fullResponse)

# Handles unexpected TCP protocol messages
def handleUnexpectedTCPProtocolMessage():
    fullResponse = AuxiliaryFunctions.encode('ERR\n')
    tcpserver.sendMessage(fullResponse)

# Receives the user requests and responses
def waitForUserMessage():
    print('waiting for TCP message')
    # waits for a request/response
    message = tcpserver.receiveMessage()
    print(message)
    if message[:3] == b'UPL':
        confirmation = message.split(b' ')
        func = allRequests.get(AuxiliaryFunctions.decode(confirmation[0]))
    else:
        confirmation = AuxiliaryFunctions.decode(message).split(' ')
        func = allRequests.get(confirmation[0])

    if func == None:
        handleUnexpectedTCPProtocolMessage()
    else:
        print('gonna call:', func)
        func(confirmation[1:])



##################
#     CS - BS    #
# (UDP Protocol) #
##################

# Sends the list of files in dirName to the CS
def sendFileList(dirName, csAddress):
    print('entrou na função sendFileList')
    try:
        newCSname = str(csAddress[0])
        newCSport = int(csAddress[1])
        print(newCSname, newCSport)
        fileListString = ''
        nFiles = 0
        with os.scandir(dirName) as it:
            print('entrou no dir')
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
        print(fullFileString)
        encodedFileString = AuxiliaryFunctions.encode(fullFileString)
        udpserver.sendMessage(newCSname, encodedFileString, newCSport)
    except ValueError:
        print('syntax error')
    except OSError as e:
        print(e)
        sys.exit(1)

# Deletes a directory from an user
def deleteDirectory(dirData, csAddress):
    try:
        userName = str(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            handleDirDeletion('NOK', csAddress)
        else:
            # if the user doesn't exist
            exists = False
            userFile = open('BSusers', 'w')  
            user = userFile.readline()
            while user:
                currentUserData = user.split()
                if currentUserData[0] == userName:
                    exists = True
                    currentDirN = currentUserData[2]
                    updatedDirN = int(currentUserData[2] - 1)
                    shutil.rmtree(dirName) # deletes the dir
                    userFile.write(str(userName) + ' ' + userPassword + ' ' + str(updatedDirN) + '\n') # updates the number of dirs of each user

                user = userFile.readline()
            userFile.close()

            if not exists:
                handleDirDeletion('NOK', csAddress)
            else:
                # now it's going to check for users with 0 dir
                userFile = open('BSusers', 'w')
                users = userFile.readlines()
                for line in users:
                    data = line.split()
                    dirN = int(data[2])
                    if dirN != 0:
                        userFile.write(line) # only writes the users with directories
                handleDirDeletion('OK', csAddress)

    except ValueError:
        handleDirDeletion('NOK', csAddress)
    except OSError as e:
        handleDirDeletion('NOK', csAddress)
        sys.exit(1)

# Adds a new user to the userList
def registerUser(userData, csAddress):
    try:
        userName = int(userData[0])
        userPassword = str(userData[1])
        if len(userData) != 2:
            # syntax error
            handleUserRegistry('ERR', csAddress)
        else:
            # checks if the user already exists
            exists = False
            userFile = open('BSusers', 'a+')  
            user = userFile.readline()
            while user:
                currentUserData = user.split()
                if currentUserData[0] == userName:
                    exists = True
                    handleUserRegistry('NOK', csAddress)
                user = userFile.readline()
            
            if not exists:
                userFile.write(str(userName) + ' ' + userPassword + ' 1\n')       
                handleUserRegistry('OK', csAddress)
                print('New user: ' + str(userName) + '\n')
            
            userFile.close()

    except ValueError:
        handleUserRegistry('ERR')
    except OSError as e:
        print('error handling the user list:',e)
        sys.exit(1)

# Handles the deregistry of the BS
def deregister():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('UNR' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)
    waitForCSMessage()
    udpserver.closeConnection() 

# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)

# Handles the CS request to list the files in a dir
def handleListFilesRequest(dirData, csAddress):
    print('entrou na função handleListFilesRequest')
    try:
        userName = str(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            print('syntax error')
        else:
            # if the user doesn't exist
            exists = False
            userFile = open('BSusers', 'r')  
            user = userFile.readline()
            while user:
                currentUserData = user.split()
                if currentUserData[0] == userName:
                    exists = True
                user = userFile.readline()
                
            if exists:
                print('existe, vai entrar em sendFileList')
                sendFileList(dirName, csAddress)
            else:
                print('User not in user list')
        
    except ValueError:
        print('syntax error')
    except OSError as e:
        print('Error handling the user list:',e)
        sys.exit(1)

# Confirmation of the user directory deletion
def handleDirDeletion(status, csAddress):
    newCSname = str(csAddress[0])
    newCSport = int(csAddress[1])
    fullResponse = AuxiliaryFunctions.encode('DBR ' + status + '\n')
    udpserver.sendMessage(newCSName, fullResponse, newCSport)
    #udpserver.sendMessage('192.168.1.65', fullResponse, 9995)

# Handles the registry response from the CS
def handleRegistryResponse(confirmation, csAddress):
    if confirmation[0] == 'OK':
        print('BS now registered in the CS')
    elif confirmation[0] == 'NOK':
        print('Registry not successfull')
    else:
        print('syntax error')

# Handles the deregistry response from the CS
def handleDeregistryResponse(confirmation, csAddress):
    if confirmation[0] == 'OK':
        print('Unregistry successfull')
    elif confirmation[0] == 'NOK':
        print('Unregistry not successfull')
    else:
        print('syntax error')

# Confirmation of the user registration
def handleUserRegistry(status, csAddress):
    newCSname = str(csAddress[0])
    newCSport = int(csAddress[1])
    fullResponse = AuxiliaryFunctions.encode('LUR ' + status + '\n')
    udpserver.sendMessage(newCSname, fullResponse, newCSport)    

# Handles unexpected UDP protocol messages
def handleUnexpectedUDPProtocolMessage():
    fullResponse = AuxiliaryFunctions.encode('ERR\n')
    udpserver.sendMessage(csName, fullResponse, csPort)

# Receives the CS requests and responses
def waitForCSMessage():
    # waits for a request
    message, address = udpserver.receiveMessage()
    confirmation = AuxiliaryFunctions.decode(message).split()
    print(confirmation[0])
    func = allRequests.get(confirmation[0])
    print(func)
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