from firstTimeConnection import firstTimeConnection
import socket
import threading
import time
import traceback


connectedPCs = []
connectedPIs = []
serverStartTime = time.time()

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
			print("{}\tRecieved message of size {}b from {}".format(round(time.time() - serverStartTime, 1), length, piAddr))
			left = length
			while left != 0:
				batch = min(1024*1024, left)
				newpart = connection.recv(batch)
				left -= len(newpart)
				b += newpart
				print("{}\t{}b out of {}b: {}%".format(round(time.time() - serverStartTime, 1), len(b),length,round((len(b)/length)*10000)/100))
			i = 0
			sent = False
			if len(connectedPCs) == 0:
				print("{}\tNo connected PC's.".format(round(time.time() - serverStartTime, 1)))
			else:
				while i < len(connectedPCs):
					c = connectedPCs[i]
					if c[0].replace("\n","") == piId.replace("\n","") or len(connectedPCs) == 1: # if they have the same ID or there is only one connected PC
						try:
							l = str(len(b) + 10000000) # add this so that the string is always the same size
							print("{}\tSending message of size {}b to {}".format(round(time.time() - serverStartTime, 1), len(b), c[0]))
							c[1].send(l.encode("utf-8"))
							c[1].sendall(b)
							sent = True
							break
						except: # this means that the PC was disconnected 
							# delete this PC from the list and try another computer
							print()
							print(traceback.format_exc())
							print("{}\t{} has disconnected.".format(round(time.time() - serverStartTime, 1), connectedPCs[i][2]))
							connectedPCs.pop(i)
							continue
					i+=1
				if not sent:
					print("{}\tThere are no connected PC's with the id [{}].".format(round(time.time() - serverStartTime, 1), piId))
					print("{}\tConnected PC's are:\n\t\t{}".format(round(time.time() - serverStartTime, 1), connectedPCs))


				
	except Exception as e:
		print(e)
		print("{}\tDisconnecting pi {}".format(round(time.time() - serverStartTime, 1), piId))


def main():
	time.sleep(1)
	print("{}\tStarting server".format(round(time.time() - serverStartTime, 1)))
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
		
		print('{}\tGot connection from {}'.format(round(time.time() - serverStartTime, 1), new_addr))
		machineType = connection.recv(1024).decode('utf-8') # this should either be PC or PI
		parts = machineType.split(",")
		if parts[0] == 'PC':
			print("{}\tIts a PC".format(round(time.time() - serverStartTime, 1)))
			connectedPCs.append([parts[1], connection, new_addr])
		elif parts[0] == 'PI':
			print("{}\tIts a PI".format(round(time.time() - serverStartTime, 1)))
			connectedPIs.append([connection, new_addr])
			t = threading.Thread(target=handlePI, args=(connection,new_addr,)) 
			t.start() 
			threads.append(t)
		else:
			print("{}\tNot a valid machine type".format(round(time.time() - serverStartTime, 1)))

		
if __name__ == '__main__':
	main()