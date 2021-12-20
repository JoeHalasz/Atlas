from firstTimeConnection import firstTimeConnection
import socket
import threading

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




def handlePI(connection):
	# get the PI's ID
	piId = getID(connection)

	
	

def main():
	threads = []
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", 17489))
	s.listen(5)
	c = []
	while True:
		# Establish connection with client. 
		connection, new_addr = s.accept()
		
		print('Got connection from', new_addr)

		t = threading.Thread(target=handlePI, args=(connection,)) 
		t.start() 

		threads.append(t)


if __name__ == '__main__':
	main()