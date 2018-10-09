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
        endConnection()
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

                fileDateString = str(fileData[argCount + 1])
                fileDate = AuxiliaryFunctions.dateEpoch(fileDateString)
                
                fileTimeString = str(fileData[argCount + 2])
                fileTime = AuxiliaryFunctions.timeEpoch(fileTimeString)
                
                fileSize = int(fileData[argCount + 3])
                data = fileData[argCount + 4]
                
                backupFile = open(fileName, 'w')
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

# Confirmation of the file backup
def handleFileBackup(status):
    fullResponse = AuxiliaryFunctions.encode('UPR ' + status + '\n')
    tcpserver.sendMessage(fullResponse)

# Confirmation of the user authentication
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

    func = allRequests.get(confirmation[0])

    if func == None:
        handleUnexpectedTCPProtocolMessage()
    else:
        return func(confirmation[1:])



##################
#     CS - BS    #
# (UDP Protocol) #
##################

# Sends the list of files in dirName to the CS
def sendFileList(dirName):
    with os.scandir(dirName) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file(): 
                print(entry.name)

# Deletes a directory from an user
def deleteDirectory(dirData):
    try:
        userName = int(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            handleDirDeletion('NOK')
        elif userName not in userList:
            handleDirDeletion('NOK')
        else:
            shutil.rmtree(dirName)
            handleDirDeletion('OK')

    except ValueError:
        handleDirDeletion('NOK')
    except OSError as e:
        handleDirDeletion('NOK')
        sys.exit(1)

# Adds a new user to the userList
def registerUser(userData):
    try:
        userName = int(userData[0])
        userPassword = str(userData[1])

        if len(userData) != 2:
            # syntax error
            handleUserRegistry('ERR')
        elif userName in userList and userList.get(userName) == userPassword:
            # if the userList was not updated
            handleUserRegistry('NOK')
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
    waitForCSMessage()
    udpserver.closeConnection() 

# Handles the registry of the new BS 
def register():
    # writes the request message
    fullRequest = AuxiliaryFunctions.encode('REG' + ' ' + bsName + ' ' + str(bsTCPPort) + '\n')
    udpserver.sendMessage(csName, fullRequest, csPort)

# Handles the CS request to list the files in a dir
def handleListFilesRequest(dirData):
    try:
        userName = int(dirData[0])
        dirName = str(dirData[1])

        if len(dirData) != 2:
            print('syntax error')
        elif userName not in userList or (userName in userList and userList.get(userName) != userPassword):
            # if the user doesn't exist or the password is wrong
            print('user error')
        else:
            # calls the function responsible for sending the file list
            sendFileList(dirName)
        
    except ValueError:
        print('syntax error')

# Confirmation of the user directory deletion
def handleDirDeletion(status):
    fullResponse = AuxiliaryFunctions.encode('DBR ' + status + '\n')
    udpserver.sendMessage(csName, fullResponse, csPort)
    #udpserver.sendMessage('192.168.1.65', fullResponse, 9995)

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
    print(func)

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
    global bsTCPPort, csName, csPort
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
        'LSF': handleListFilesRequest
    }

    bsTCPPort, csName, csPort = getArguments(argv)

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