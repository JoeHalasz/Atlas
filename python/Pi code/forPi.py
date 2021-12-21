
# later add this to crontab by doing sudo crontab -e
# @reboot python3 /home/pi/forPi.py &

import speech_recognition as sr
import threading
import paramiko
import os
import traceback
import time 
from os.path import exists
import socket

r = sr.Recognizer()
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording
audio = [""]

def saveAudio(audio, x):
	if audio != "":
		with open("sound"+str(x)+".wav", "wb") as f:
			f.write(audio.get_wav_data())

def sendAudio(sftp, x):
	print("sending audio", x)
	try:
		sftp.put("sound"+str(x)+".wav", "autorun/audioFiles/sound"+str(x)+".wav")
	except FileNotFoundError:
		pass # this means that the file was deleted too quickly for SFTP to react. Doesn't matter at all
	os.remove("sound"+str(x)+".wav") # delete after use


def listen(source, audio):
	audio[0] = r.listen(source)
	# while True:

	# 	try:
			
	# 		break
	# 	except:
	# 		print("Listening error")
	# 		pass


def getId(server):
	try:
		with open("id.txt", "r") as f:
			piId = f.readline()
			server.send(piId.encode('utf-8'))
			piId = server.recv(1024).decode('utf-8')
	except Exception:
		server.send("-1".encode('utf-8'))
		piId = server.recv(1024).decode('utf-8')
		with open("id.txt", "w") as f:
			f.write(piId)
	print("My ID is", piId)
	return piId

	


def main():
	print("trying to connect")
	serverIp = "192.168.1.241"
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((serverIp, 17489))
	server.send("PI".encode('utf-8'))

	piId = getId(server)
	print(piId)

	with sr.Microphone() as source:
		x = 0
		print("Listening")
		# audio[0] = r.listen(source)
		while True:
			listen(source,audio)
			# t = threading.Thread(target=listen, args=(source,audio,))
			# t.start()
			
			saveAudio(audio[0], x)
			sendAudio(sftp, x)
			audio[0] = ""
			
			x += 1
			# t.join()



if __name__ == '__main__':
	main()
