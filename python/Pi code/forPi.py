
# later add this to crontab by doing sudo crontab -e
# @reboot python3 /home/pi/forPi.py &

import speech_recognition as sr
import threading
import paramiko
import os
import traceback
import time 

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




def main():
	print("trying to connect")
	for x in range(10):
		try: # connect to PC
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
			ssh.connect("192.168.1.240","22","jhala","Tigerandzues")
			sftp = ssh.open_sftp()
			break
		except: # this will fail if the PC is not in the same network. 
			print("Could not connect")
			time.sleep(5)
		if x == 9:
			quit()

	print("connected")
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
	try:
		main()
	except:
		print(traceback.format_exc())
		f = open("/home/pi/error.txt", "w+")
		f.write(traceback.format_exc())
		f.close()

