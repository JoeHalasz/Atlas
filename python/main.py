import speech_recognition as sr
import threading
from pynput.keyboard import Key, Controller
# more keys here: https://pythonhosted.org/pynput/keyboard.html#pynput.keyboard.Key
from word2number import w2n


r = sr.Recognizer()
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording

stop = False
commands = ["open", "start taking note", "take a note", 
			"write this down", "type this", "stop listening", 
			"start typing", "press enter", "save",
			"close window", "refresh page"]

stopTypingTriggers = ["stop writing", "stop typing", "end note", "stop taking note"]

audio = [""]
typing = False

keys = Controller()


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



def textTransform(audio, r):
	global typing
	try:
		if audio != "":
			text = r.recognize_google(audio)
			# r.recognize_sphinx(audio) # this is offline 
			if text == "stop listening":
				print("Good Bye")
				quit()
			if text != "":
				print(text)
				if typing:
					typeWords(text)
				elif len(text) > 1:
					text = text.lower()
					for c in commands:
						if c in text:
							helper = text.split(c + " ", 1)
							command = c
							commandParams = ""
							if len(helper) > 1:
								commandParams = helper[1]
							if command == "open":
								t = threading.Thread(target=openApplication, args=(commandParams,))
								t.start()
							elif command == "start taking note" or command == "write this down" or command == "take a note":
								openApplication("sublime")
								t = threading.Thread(target=openApplication, args=("sublime",))
								t.start()
								typing = True
								if commandParams != "": # type anything they say after the command if its not in another sentence
									typeWords(commandParams)
							elif command == "type this" or command == "start typing":
								typing = True
								if commandParams != "": # type anything they say after the command if its not in another sentence
									typeWords(commandParams)
							elif command == "save":
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
							break; 

	except sr.UnknownValueError as e:
		pass
	


def saveAudio(audio, num):
	if audio != "":
		with open("microphone-results" + str(num) + ".wav", "wb") as f:
			f.write(audio.get_wav_data())


def listen(source, audio):
	while True:
		try:
			audio[0] = r.listen(source)
			break
		except:
			print("Listening error")
			pass


with sr.Microphone() as source:
	x = 0
	audio[0] = r.listen(source)
	while True:
		t = threading.Thread(target=listen, args=(source,audio,))
		t.start()
		
		textTransform(audio[0], r)
		# saveAudio(audio[0], x)
		audio[0] = ""
		
		x += 1
		t.join()

