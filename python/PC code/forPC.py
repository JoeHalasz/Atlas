import speech_recognition as sr
import threading
from pynput.keyboard import Key, Controller
# more keys here: https://pythonhosted.org/pynput/keyboard.html#pynput.keyboard.Key
from word2number import w2n
import os
import traceback

import datetime
from parsing import *
import socket
import time

import applicationStuff


r = sr.Recognizer()
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording

stop = False
commands = ["open", "start taking note", "take a note", 
			"write this down", "type this", "stop listening", 
			"start typing", "press enter", "save", "press tab",
			"close window", "refresh page", # 
			"remind me to", "I have to","you have to","from my schedule","from my calendar", # calendar commands
			"close tab", "close this tab", "close a tab", "close the tab", # browser commands
			"tab to", "alt tab to"
			]

stopTypingTriggers = ["stop writing", "stop typing", "end note", "stop taking note"]

audio = [""]
typing = False

keys = Controller()
x = 0


# this function will type out the passed in wordss
# it will also parse things like 
# next line, press enter, delete word and press backspace.
def typeWords(words):
	global typing
	done = False

	for s in stopTypingTriggers:
		if s in fixText(words):
			done=True
			words = words.lower().replace(s, "")

	words = words.replace("next line", "next_line")
	words = words.replace("press enter", "next_line")
	words = words.replace("delete word", "delete_word")
	words = words.replace("press backspace", "delete_word")
	# words = words.replace(". ", ".")
	words = words.replace("Txt", "txt")
	wordsList = words.split(" ")
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
			
	for x, word in enumerate(wordsList):
		if word == "next_line":
			keys.press(Key.enter)
			keys.release(Key.enter)
		elif word == "delete_word":
			keys.press(Key.ctrl_l)
			keys.press(Key.backspace)
			keys.release(Key.ctrl_l)
			keys.release(Key.backspace)
		else:
			keys.type(word)
			if x != len(wordsList) - 1:
				keys.press(Key.space)
				keys.release(Key.space)

	if done:
		typing = False
	else:
		keys.press(Key.enter)
		keys.release(Key.enter)

# this fucntion will remove punctuation and make sure the text is all lowercase
def fixText(text):
	if len(text) == 0:
		return ""
	if text[-1] == "." or text[-1] == "!" or text[-1] == "?":
		text = text[:-1]
	return text.lower().replace(",","")


# this function checks the passed in text against the list of 
# commands and if one is found will run that command on it 
# some commands start threads and others run on the main thread
def textTransform(text):
	global typing
	oldText = text
	text = fixText(text)
	if text != None:
		if text == "stop listening":
			print("Good Bye")
			raise Exception("Quit")
		if text != "":
			print(text)
			if typing:
				typeWords(oldText)
			elif len(text) > 1:
				text = text.lower()
				noCommandFound = True
				for c in commands:
					if c.lower() in text: # if any of the commands are in the text
						noCommandFound = False
						helper = text.split(c + " ", 1)
						command = c
						commandParams = ""
						if len(helper) > 1:
							commandParams = helper[1]
						if command == "open":
							t = threading.Thread(target=applicationStuff.openApplication, args=(commandParams,keys,))
							t.start()
						elif command == "start taking note" or command == "write this down" or command == "take a note":
							t = threading.Thread(target=applicationStuff.openApplication, args=("sublime",keys,))
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
						elif command == "press tab":
							keys.press(Key.tab)
							keys.release(Key.tab)
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
						elif command == "from my schedule" or command == "from my calendar":
							removeFromScheduleParsing(text, command)
						elif command == "close tab" or command == "close this tab" or command == "close a tab":
							keys.press(Key.ctrl_l)
							keys.press("w")
							keys.release(Key.ctrl_l)
							keys.release("w")
						elif command == "tab to" or command == "alt tab to":
							applicationStuff.bringToForground(text.split(command)[-1], keys, True)
						break
				if noCommandFound:
					if text.split(" ")[0] == "type":
						typeWords(" ".join(text.split(" ")[1:]))


# this function will save the audio.
# it will use the num passed in as a part of the file name
def saveAudio(audio, num):
	if audio != "":
		with open("microphone-results" + str(num) + ".wav", "wb") as f:
			f.write(audio.get_wav_data())


# this function will use the server connection and attempt to 
# get data from the server. 
# if the connection is broken it will return "reconnect"
# if data is successfully downloaded from the server it will decode 
# the data and return it as a string
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
		time.sleep(.01)


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
	

# this function will start the event thread for Google Calendar
# then connect to the server
# then continuously get data from the server, and process that data.
def main():
	run_event = threading.Event()
	run_event.set()

	server = serverConnection()

	t = threading.Thread(target=Events.createTimedEvents, args=(run_event,))
	t.start()
	
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

