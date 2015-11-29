# Group Member: Brendon Hollingsworth, Jarid Goodwin, Jacob Goodwin

import sys
import socket
# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):
	# The buffer
	recvBuff = ""

	# The temporary buffer
	tmpBuff = ""

	# Keep receiving till all is received
	while len(recvBuff) < numBytes:

		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes).decode('ascii')  #had to add .decode for it to work

		# The other side has closed the socket
		if not tmpBuff:
			break



		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	return recvBuff

#from ephemeral.py, not entirely sure how to use it yet
def getEphemeralSock():
	# Create a socket
	welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to port 0
	welcomeSocket.bind(('',0))
	return welcomeSocket



def put(dataSock, fileName):
	#need to check if file name is valid
	# Open the file
	fileObj = open(fileName, "r")
	# The number of bytes sent
	numSent = 0
	# The file data
	fileData = None
	# Keep sending until all is sent
	while True:
		# Read 65536 bytes of data
		fileData = fileObj.read(65536)
		# Make sure we did not hit EOF
		if fileData:
			# Get the size of the data read
			# and convert it to string
			dataSizeStr = str(len(fileData))
			# Prepend 0's to the size string
			# until the size is 10 bytes
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr
			# Prepend the size of the data to the
			# file data.
			fileData = dataSizeStr + fileData
			# The number of bytes sent
			numSent = 0
			# Send the data!
			while len(fileData) > numSent:
				numSent += dataSock.send(fileData.encode('ascii'))
		# The file has been read. We are done
		else:
			break


	print("Sent ", numSent, " bytes.")

	# Close the socket and the file
	dataSock.close()
	fileObj.close()

def get(dataSock, fileName):
	fileData = ""
	recvBuff = ""
	fileSize = 0
	fileSizeBuff = ""
	fileSizeBuff = recvAll(dataSock, 10)
	fileSize = int(fileSizeBuff)
	fileData = recvAll(dataSock, fileSize)
	print("The file data is: ")
	print(fileData)
	dataSock.close()
	f = open(fileName, 'w')
	f.write(fileData)
	print(fileName, "has been saved.")

def ls(dataSock):
	fileData = ""
	recvBuff = ""
	fileSize = 0
	fileSizeBuff = ""
	fileSizeBuff = recvAll(dataSock, 10)
	fileSize = int(fileSizeBuff)
	fileData = recvAll(dataSock, fileSize)
	print(fileData)
	dataSock.close()

def sendCommand(commandString, connSock):
	# send command
	size = str(len(commandString))
	# Prepend 0's to the size string
	# until the size is 2 bytes
	while len(size) < 2:
		size = "0" + size
	commandString = size + " " + commandString   #prepend size of command string
	bytes_sent = 0
	while bytes_sent < len(commandString):
		bytes_sent += connSock.send(commandString.encode('ascii'))



def main(argv):

	# Command line checks
	if len(argv) < 2:
		print("USAGE python " + argv[0] + " <FILE NAME>")

	while True:


		# Server address
		serverAddr = argv[1]

		# Server port
		serverPort = int(argv[2])

		# Create a TCP socket
		connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect to the server
		connSock.connect((serverAddr, serverPort))

		commandString = input("ftp> ")
		command = commandString.split()   #splits string into list of words



		if(command[0].lower() == "get"):
			welcomeSock = getEphemeralSock()
			commandString = commandString + " " + str(welcomeSock.getsockname()[1])
			welcomeSock.listen(1)
			sendCommand(commandString, connSock)
			dataSock, addr = welcomeSock.accept()
			get(dataSock, command[1])
		elif(command[0].lower() == "put"):
			welcomeSock = getEphemeralSock()
			commandString = commandString + " " + str(welcomeSock.getsockname()[1])
			welcomeSock.listen(1)
			sendCommand(commandString, connSock)
			dataSock, addr = welcomeSock.accept()
			put(dataSock, command[1])
		elif(command[0].lower() == "ls"):
			welcomeSock = getEphemeralSock()
			commandString = commandString + " " + str(welcomeSock.getsockname()[1])
			welcomeSock.listen(1)
			sendCommand(commandString, connSock)
			dataSock, addr = welcomeSock.accept()
			ls(dataSock)
		elif(command[0].lower() == "quit"):
			sendCommand(commandString, connSock)
			sys.exit(1)
		else:
			print("Invalid command")



if __name__ == "__main__":
	main(sys.argv)