from firstTimeConnection import firstTimeConnection
import socket
import threading
import time

connectedPCs = []
connectedPIs = []


# this will get the PI's id or create one for it if it doesnt have one, and send it back to the pi
def getID(connection):
	data = connection.recv(1024) # should be just an ID
	if data:
		data = data.decode('utf-8')
		print(data)
		if data == "-1":
			piId = str(firstTimeConnection())
		else:
			piId = data

		connection.send(piId.encode('utf-8'))
		return piId


# def handlePC(connection):
# 	global connectedPCs
# 	global connectedPIs
# 	connection.settimeout(5) # 5 seconds
# 	try:
# 		while True:
# 			print("sending")
# 			connection.send("connected?".encode('utf-8'))
# 			print("waiting for recv")
# 			data = connection.recv(1024)
# 			print(connectedPCs)
# 	except: # this means that it disconnected
# 		print("disconnected")
# 		for i in range(len(connectedPCs)): # remove it from the connected lists
# 			c = connectedPCs[i]
# 			if c[0] == connection:
# 				connectedPCs.pop(i)
# 	print(connectedPCs)


def handlePI(connection):
	try:
		global connectedPCs
		global connectedPIs
		# get the PI's ID
		piId = getID(connection)
		# check if that ID has any computers to connect to
		while True:
				strlen = connection.recv(8).decode("utf-8")
				length = int(strlen) - 10000000 # added this so that the bytes size is always the same 
				print(length)
				b = b''
				while len(b) < length:
					batch = min(4096, length)
					newpart = connection.recv(batch)
					b += newpart
					print("{}kb out of {}kb: {}%".format(round(len(b)/1024,1),round(length/1024,1),round((len(b)/length)*10000)/100))

				
	except Exception as e:
		print(e)
		print("Disconnecting pi",piId)




def main():
	print("Starting server")
	global connectedPCs
	global connectedPIs
	threads = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("192.168.1.241", 51152))
	s.listen(5)
	c = []
	while True:
		# Establish connection with client. 
		connection, new_addr = s.accept()
		
		print('Got connection from', new_addr)
		machineType = connection.recv(1024).decode('utf-8') # this should either be PC or PI
		parts = machineType.split(",")
		if parts[0] == 'PC':
			print("Its a PC")
			connectedPCs.append([parts[1], connection, new_addr])

			# t = threading.Thread(target=handlePC, args=(connection,))
			# t.start()
			# threads.append(t)
			while True:
				connection.send("here".encode('utf-8'))
				print("sent")
				time.sleep(1)
		elif parts[0] == 'PI':
			print("Its a PI")
			connectedPIs.append([connection, new_addr])
			t = threading.Thread(target=handlePI, args=(connection,)) 
			t.start() 
			threads.append(t)
		else:
			print("Not a valid machine type")

		


if __name__ == '__main__':
	main()



	# print("trying to connect")
	# try: # connect to PC
	# 	ssh = paramiko.SSHClient()
	# 	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
	# 	ssh.connect("192.168.1.240","22","jhala","Tigerandzues")
	# 	sftp = ssh.open_sftp()
	# except: # this will fail if the PC is not in the same network. 
	# 	print("Could not connect")
	# 	quit()

	# print("connected")
