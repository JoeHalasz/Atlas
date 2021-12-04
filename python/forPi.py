# later add this to crontab by doing sudo crontab -e
# then putting this at the bottom 
# @reboot python3 /home/pi/Desktop/exemple.py &

# if this doesnt work ( it probably wont ) then go to this site 
# https://raspberrypi.stackexchange.com/questions/8734/execute-script-on-start-up


import threading
from word2number import w2n
import paramiko



def typeWords(words):
	global typing
	if sshWorked:
		stdin, stdout, stderr = ssh.exec_command('python autorun/typeWords.py "' + words + '"')

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
	if sshWorked:
		stdin, stdout, stderr = ssh.exec_command('python autorun/openProcess.py "' + commandParams + '"')



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



try: # connect to PC
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
	ssh.connect("172.20.4.29","22","jhala","Tigerandzues")
except: # this will fail if the PC is not in the same network. 
	sshWorked = False

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



# word to vec
# spacy