from firstTimeConnection import firstTimeConnection
import socket
import threading
from datetime import datetime
import time
import traceback


connectedPCs = []
connectedPIs = []

# this will get the PI's id or create one for it if it doesnt have one, and send it back to the pi
def getID(connection):
	data = connection.recv(1024) # should be just an ID
	if data:
		data = data.decode('utf-8')
		if data == "-1":
			piId = str(firstTimeConnection())
		else:
			piId = data

		connection.send(piId.encode('utf-8'))
		return piId


def getTime():
	return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def handlePI(connection, piAddr):
	try:
		global connectedPCs
		global connectedPIs
		# get the PI's ID
		piId = getID(connection)
		# check if that ID has any computers to connect to
		while True:
			strlen = connection.recv(8).decode("utf-8")
			length = int(strlen) - 10000000 # added this so that the bytes size is always the same 
			b = b''
			print("{}\tRecieved message of size {}b from {}".format(getTime(), length, piAddr))
			left = length
			while left != 0:
				batch = min(1024*1024, left)
				newpart = connection.recv(batch)
				left -= len(newpart)
				b += newpart
				print("{}\t{}b out of {}b: {}%".format(getTime(), len(b),length,round((len(b)/length)*10000)/100))
			i = 0
			sent = False
			if len(connectedPCs) == 0:
				print("{}\tNo connected PC's.".format(getTime()))
			else:
				while i < len(connectedPCs):
					c = connectedPCs[i]
					if c[0].replace("\n","") == piId.replace("\n","") or len(connectedPCs) == 1: # if they have the same ID or there is only one connected PC
						try:
							l = str(len(b) + 10000000) # add this so that the string is always the same size
							print("{}\tSending message of size {}b to {}".format(getTime(), len(b), c[0]))
							c[1].send(l.encode("utf-8"))
							c[1].sendall(b)
							sent = True
							break
						except: # this means that the PC was disconnected 
							# delete this PC from the list and try another computer
							# print()
							# print(traceback.format_exc())
							print("{}\t{} has disconnected.".format(getTime(), connectedPCs[i][2]))
							connectedPCs.pop(i)
							continue
					i+=1
				if not sent:
					print("{}\tThere are no connected PC's with the id [{}].".format(getTime(), piId))
					print("{}\tConnected PC's are:\t{}".format(getTime(), connectedPCs))


				
	except Exception as e:
		print(e)
		print("{}\tDisconnecting pi {}".format(getTime(), piId))


def main():
	time.sleep(1)
	print("{}\tStarting server".format(getTime()))
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
		
		print('{}\tGot connection from {}'.format(getTime(), new_addr))
		machineType = connection.recv(1024).decode('utf-8') # this should either be PC or PI
		parts = machineType.split(",")
		if parts[0] == 'PC':
			print("{}\tIts a PC".format(getTime()))
			connectedPCs.append([parts[1], connection, new_addr])
		elif parts[0] == 'PI':
			print("{}\tIts a PI".format(getTime()))
			connectedPIs.append([connection, new_addr])
			t = threading.Thread(target=handlePI, args=(connection,new_addr,)) 
			t.start() 
			threads.append(t)
		else:
			print("{}\tNot a valid machine type".format(getTime()))

		
if __name__ == '__main__':
	main()