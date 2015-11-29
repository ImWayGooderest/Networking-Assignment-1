# Group Members: Brendon Hollingsworth, Jarid Goodwin, Jacob Goodwin

import sys
import socket
import subprocess
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
		tmpBuff =  sock.recv(numBytes).decode('ascii')  #had to add.decode for it to work

		# The other side has closed the socket
		if not tmpBuff:
			break



		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	return recvBuff


def put(fileName, dataSock):


	# The buffer to all data received from the
	# the client.
	fileData = ""
	# The temporary buffer to store the received
	# data.
	recvBuff = ""
	# The size of the incoming file
	fileSize = 0
	# The buffer containing the file size
	fileSizeBuff = ""
	# Receive the first 10 bytes indicating the
	# size of the file
	fileSizeBuff = recvAll(dataSock, 10)
	# Get the file size
	fileSize = int(fileSizeBuff)
	print("The file size is ", fileSize)
	# Get the file data
	fileData = recvAll(dataSock, fileSize)
	print(fileName,"received.")
	print("The file data is: ")
	print(fileData)

def get(fileName, dataSock):
	fileObj = open(fileName, "r")
	numSent = 0
	fileData = None
	while True:
		fileData = fileObj.read(65536)
		if fileData:
			dataSizeStr = str(len(fileData))
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr
			fileData = dataSizeStr + fileData
			numSent = 0
			while len(fileData) > numSent:
				numSent += dataSock.send(fileData.encode('ascii'))
		else:
			break
	print(fileName,"sent.")
	print("Sent", numSent, " bytes.")
	dataSock.close()
	fileObj.close()

def ls(dataSock):
	lsData = ""
	#if windows use dir instead of ls -l
	if sys.platform == "win32":
		for line in subprocess.getstatusoutput('dir'):
			lsData += str(line)
	else:
		for line in subprocess.getstatusoutput('ls -l'):
			lsData += str(line)

	dataSizeStr = str(len(lsData))
	# Prepend 0's to the size string
	# until the size is 10 bytes
	while len(dataSizeStr) < 10:
		dataSizeStr = "0" + dataSizeStr
	# Prepend the size of the data to the
	# file data.
	lsData = dataSizeStr + lsData
	# The number of bytes sent
	numSent = 0
	# Send the data!
	while len(lsData) > numSent:
		numSent += dataSock.send(lsData.encode('ascii'))
	print("Data sent.")

def getCommand(sock):
	commandBytes = int(recvAll(sock,3))	#receive 1st 3 bytes (2-byte number and a space) indicating command size
	return recvAll(sock, commandBytes)	#receive the remaining command

def main(argv):
	if len(argv) > 1:
		# Accept connections forever
		# The port on which to listen
		listenPort = int(argv[1])

		# Create a welcome socket.
		welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind the socket to the port
		welcomeSock.bind(('', listenPort))

		# Start listening on the socket
		welcomeSock.listen(1)
		while True:
			print ("Waiting for connections...")

			# Accept connections
			clientSock, addr = welcomeSock.accept()

			print ("Accepted connection from client: ", addr)
			print ("\n")
			clientCommand = getCommand(clientSock)
			clientCommand = clientCommand.split()

			if(clientCommand[0].lower() == "get"):
				print("Received get command. Preparing to send file.")
				dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataSock.connect((addr[0], int(clientCommand[-1])))	#addr[0] is the address the last socket connected to, clientCommand[2] is the ephemeral port sent by client
				get(clientCommand[1], dataSock)
			elif(clientCommand[0].lower() == "put"):
				print("Received put command. Preparing to receive file.")
				dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataSock.connect((addr[0], int(clientCommand[-1])))	#addr[0] is the address the last socket connected to, clientCommand[2] is the ephemeral port sent by client
				put(clientCommand[1], dataSock)
			elif(clientCommand[0].lower() == "ls"):
				print("Received ls command. Preparing to send folder contents.")
				dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataSock.connect((addr[0], int(clientCommand[-1])))	#addr[0] is the address the last socket connected to, clientCommand[2] is the ephemeral port sent by client
				ls(dataSock)
			elif(clientCommand[0].lower() == "quit"):
				print(addr," has closed their session")




if __name__ == "__main__":
	main(sys.argv)