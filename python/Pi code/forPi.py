
# later add this to crontab by doing sudo crontab -e
# @reboot python3 "/home/pi/Atlas/python/Pi code/forPi.py" &

import speech_recognition as sr
import threading
import paramiko
import os
import traceback
import time 
from os.path import exists
import socket
import pocketsphinx




r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.energy_threshold = 2000
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording
audio = [""]


# this function will save the audio using x in the filename
def saveAudio(audio, x):
	if audio != "":
		with open("sound"+str(x)+".wav", "wb") as f:
			f.write(audio.get_wav_data())


# this function will listen for audio, make that audio into text
# then send the text to the server 
def getTextAndSend(server,audio,reconnect, r,x):
	try:
		text = r.recognize_google(audio)
		# text = r.recognize_wit(audio,"ZKH4OYXN4M4WE5YFUACWZLBJRXY66UHF") # this is better than google, but it takes longer
		# text = r.recognize_sphinx(audio) # this is offline
		send(server,text)
		# saveAudio(audio,x)
	except sr.UnknownValueError: # sometimes if the audio is empty this happens
		pass
	except ConnectionResetError: # this means there was a server disconnect
		reconnect = True


# this fucntion will send text to the server
def send(server, send):
	b = send # do this just incase audio gets overwritten in main
	# b = audio.get_raw_data()
	l = str(len(b) + 10000000) # add this so that the string is always the same size
	print("Sending message of size {}b".format(len(b)))
	server.send(l.encode("utf-8"))
	server.send(b.encode("utf-8"))
	

# this function will get this PI's ID, and if it doesnt have one,
# it will get a new one from the server
def getId(server):
	try:
		with open("id.txt", "r") as f:
			piId = f.readline().replace("\n","")
			server.send(piId.encode('utf-8'))
			piId = server.recv(1024).decode('utf-8')
	except Exception:
		server.send("-1".encode('utf-8'))
		piId = server.recv(1024).decode('utf-8')
		with open("id.txt", "w") as f:
			f.write(piId)
	piId = piId.replace("\n","")
	print("My ID is", piId)
	return piId


# this function will connect to the server and get the PiId
def serverConnection():
	server = None
	tries = 0
	while True:
		try:
			print("trying to connect")
			serverIp = "71.105.82.137"
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.connect((serverIp, 51152))
			server.send("PI".encode('utf-8'))
			piId = getId(server)
			return server,piId
		except:
			tries += 1
			print(traceback.format_exc())
			print("Try", tries)
			time.sleep(1)


# this function will connect to the server 
# then continuously listen for audio
# convert that audio to text 
# then send it to the server 
def main():	
	server, piId = serverConnection()
	print(piId)
	reconnect = False
	while True:
		try:
			with sr.Microphone() as source:
				r.adjust_for_ambient_noise(source, duration=1)
				print("Listening")
				x = 0
				while True:
					if reconnect:
						server, piId = serverConnection()
						reconnect = False
					audio = r.listen(source)

					t = threading.Thread(target=getTextAndSend, args=(server,audio,reconnect,r,x,))
					t.start()
		except:
			if "Stream closed" in traceback.format_exc():
				# this means that the mic was unplugged
				continue
			else:
				break

if __name__ == '__main__':
	main()
