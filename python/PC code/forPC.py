import speech_recognition as sr
import threading
from pynput.keyboard import Key, Controller
import subprocess
# more keys here: https://pythonhosted.org/pynput/keyboard.html#pynput.keyboard.Key
from word2number import w2n
import os
import traceback

import datetime
from parsing import *
import socket

r = sr.Recognizer()
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording

stop = False
commands = ["open", "start taking note", "take a note", 
			"write this down", "type this", "stop listening", 
			"start typing", "press enter", "save",
			"close window", "refresh page", # 
			"remind me to", "I have to","you have to" # calendar commands
			]

stopTypingTriggers = ["stop writing", "stop typing", "end note", "stop taking note"]

audio = [""]
typing = False

keys = Controller()
x = 0


def typeWords(words):
	global typing
	done = False

	for s in stopTypingTriggers:
		if s in words:
			done=True
			words = words.replace(s, "")
	
	words = words.replace("next line", "next_line")
	words = words.replace("press enter", "next_line")
	words = words.replace("delete word", "delete_word")
	words = words.replace("press backspace", "delete_word")
	words = words.replace(". ", ".")
	words = words.replace("Txt", "txt")
	wordsList = words.split(" ")
	print(wordsList)
	if "delete" in wordsList: # check if user said "delete N words"
		place = wordsList.index("delete")
		try:
			number = w2n.word_to_num(wordsList[place+1]) 
			x = 0
			while x < int(number):
				keys.press(Key.ctrl_l)
				keys.press(Key.backspace)
				keys.release(Key.ctrl_l)
				keys.release(Key.backspace)
				x += 1
			return
		except:
			pass

	for word in wordsList:
		if word == "next_line":
			keys.press(Key.enter)
			keys.release(Key.enter)
		elif word == "delete_word":
			keys.press(Key.ctrl_l)
			keys.press(Key.backspace)
			keys.release(Key.ctrl_l)
			keys.release(Key.backspace)
		else:
			letters = list(word)
			for l in letters:
				keys.press(l)
				keys.release(l)
			if len(letters) > 0:
				keys.press(Key.space)
				keys.release(Key.space)
	keys.press(Key.enter)
	keys.release(Key.enter)
	if done:
		typing = False;
		


# TODO better way to do this might be to press the windows key and type it then press enter
def openApplication(commandParams):
	if "chrome" in commandParams:
		subprocess.call('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
	elif "sublime" in commandParams:
		subprocess.call('C:\\Program Files\\Sublime Text 3\\sublime_text.exe')
	elif "brave" in commandParams:
		subprocess.call('C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe')
	elif "git" in commandParams:
		subprocess.call('C:\\Users\\jhala\\AppData\\Local\\GitHubDesktop\\GitHubDesktop.exe')
	elif "unity" in commandParams:
		subprocess.call('C:\\Program Files\\Unity Hub\\Unity Hub.exe')


# def getText(audio, r):
# 	try:
# 		if audio != "":
# 			text = r.recognize_google(audio) # this line will error if the download has not finished yet.
# 			# text = r.recognize_sphinx(audio) # this is offline 
# 			return text
# 	except sr.UnknownValueError as e:
# 		pass
# 	return None


def textTransform(text):
	global typing
	if text != None:
		if text == "stop listening":
			print("Good Bye")
			raise Exception("Quit")
		if text != "":
			print(text)
			if typing:
				typeWords(text)
			elif len(text) > 1:
				text = text.lower()
				for c in commands:
					if c.lower() in text: # if any of the commands are in the text
						helper = text.split(c + " ", 1)
						command = c
						commandParams = ""
						if len(helper) > 1:
							commandParams = helper[1]
						if command == "open":
							t = threading.Thread(target=openApplication, args=(commandParams,))
							t.start()
						elif command == "start taking note" or command == "write this down" or command == "take a note":
							t = threading.Thread(target=openApplication, args=("sublime",))
							t.start()
							typing = True
							if commandParams != "": # type anything they say after the command if its not in another sentence
								typeWords(commandParams)
						elif command == "type this" or command == "start typing":
							typing = True
							if commandParams != "": # type anything they say after the command if its not in another sentence
								typeWords(commandParams)
						elif command == "save" and text == "save":
							keys.press(Key.ctrl_l)
							keys.press("s")
							keys.release(Key.ctrl_l)
							keys.release("s")
						elif command == "press enter":
							keys.press(Key.enter)
							keys.release(Key.enter)
						elif command == "close window":
							keys.press(Key.alt)
							keys.press(Key.f4)
							keys.release(Key.alt)
							keys.release(Key.f4)
						elif command == "refresh page":
							keys.press(Key.f5)
							keys.release(Key.f5)
						elif command == "remind me to" or command == "I have to" or command == "you have to":
							remindMeToParsing(text, command)
						break;




def saveAudio(audio, num):
	if audio != "":
		with open("microphone-results" + str(num) + ".wav", "wb") as f:
			f.write(audio.get_wav_data())


def getData(server):
	while True:
		try:
			strlen = server.recv(8).decode("utf-8")
			length = int(strlen) - 10000000 # added this so that the bytes size is always the same 
			b = b''
			left = length
			while left != 0:
				batch = min(1024*1024, left)
				newpart = server.recv(batch)
				left -= len(newpart)
				b += newpart
				# print("{}b out of {}b: {}%".format(len(b),length,round((len(b)/length)*10000)/100))
			return b.decode('utf-8')
		except ConnectionResetError:
			return "reconnect"
		except Exception:
			e = traceback.format_exc()
			if "timeout" in e:
				pass
			else:
				print(e)
	


# def readAudioOld():
# 	global x
# 	path = os.path.expanduser('~') + "\\autorun\\audioFiles"
# 	paths = []
# 	while len(paths) == 0: # wait until there is something in the folder
# 		paths = os.listdir(path)
	
# 	# get the one path we want to process this time 
# 	path = path + "\\" + paths[0]
# 	# print("checking", path)
# 	while True:
# 		try:
# 			with open(path, "rb") as f:
# 				data = f.read()
# 			os.remove(path) # only delete the file if the audio came back as a real audio file.
# 			return sr.AudioData(data, 44100, 2)
# 		except PermissionError:
# 			# print("waiting for download")
# 			pass



def main2():
	run_event = threading.Event()
	run_event.set()
	t = threading.Thread(target=Events.createTimedEvents, args=(run_event, 1))
	t.start()
	# add [name] to my calendar for tomorrow
	# add [name] to tomorrows schedule at 8am
	# add [name] tomorrow from 8 to 10am
	# remind me to [name] in 2 days 
	# remind me to [name] on the 5th
	# calendarAdd("thing", "on 12/07/21")
	# calendarRemove("do homework")
	import time
	time.sleep(.5)

	run_event.clear()
	t.join()



# will return the username of this user if it exists
def getID():
	try:
		with open("id.txt", "r") as f:
			return f.read().replace("\n","")
	except: # this means that the id file doesnt exist
		return ""


# this will connect to the server and ensure that the server knows we are still connected
def serverConnection():
	server = None
	while True: # try to connect
		try:
			print("Trying to connect to server")
			serverIp = "71.105.82.137"
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.settimeout(5) # 5 seconds need this so that ctrl c works
			server.connect((serverIp, 51152))
			server.send("PC,{}".format(getID()).encode('utf-8'))
			return server
		except:
			print(traceback.format_exc())
	


def main():

	run_event = threading.Event()
	run_event.set()

	server = serverConnection()

	t = threading.Thread(target=Events.createTimedEvents, args=(run_event,))
	t.start()

	# calendarAdd("Get new parking permit", "December 30", "9am")
	# calendarRemove("Something")
	
	try:
		while True:
			text = getData(server)
			if audio == 'reconnect':
				server = serverConnection()
				continue
			textTransform(text)
			# saveAudio(audio, x)

	except KeyboardInterrupt as e:
		pass
	except:
		print(traceback.format_exc())
	print("Stopping event thread")
	run_event.clear()

	t.join()
	


if __name__ == '__main__':
	main()