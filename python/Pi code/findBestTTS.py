
import speech_recognition as sr
import threading
import paramiko
import os
import traceback
import time 
from os.path import exists
import socket
import pocketsphinx


def fixText(text):
	return text.lower().replace(".","").replace(",","").replace("?","").replace("!","")



corrects = {}
corrects["google"] = 0
corrects["wit"] = 0
total = 0


r = sr.Recognizer()
r.pause_threshold = 0.3  # seconds of non-speaking audio before a phrase is considered complete
r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.1  # seconds of non-speaking audio to keep on both sides of the recording

with sr.Microphone() as source:
	print("Listening")
	x = 0
	while True:
		print()
		audio = r.listen(source)
		try:
			before = time.time()
			google = r.recognize_google(audio)
			print("Google done, took {} seconds".format(time.time() - before))
			before = time.time()
			wit = r.recognize_wit(audio,"ZKH4OYXN4M4WE5YFUACWZLBJRXY66UHF")
			print("Wit done, took {} seconds".format(time.time() - before))
			print("Google:[{}]".format(fixText(google)))
			print("Wit:   [{}]".format(fixText(wit)))
			if fixText(google) == fixText(wit):
				print("Google and wit have the same output")
				while True:
					i = fixText(input("Were they correct?"))
					if i == "y" or i == "yes":
						corrects["google"] += 1
						corrects["wit"] += 1
						break
					elif i == "n" or i == "no":
						break
					elif i == "d" or i == "delete":
						total -= 1
						break
			else:
				while True:
					i = fixText(input("Type which one was correct"))
					if i == "google":
						corrects["google"] += 1
						break
					elif i == "wit":
						corrects["wit"] += 1
						break
					elif i == "n" or i == "neither" or i == "no":
						break
					elif i == "b" or i == "both":
						corrects["google"] += 1
						corrects["wit"] += 1
						break

			total += 1
			if fixText(google) == "end":
				break
					
		except sr.UnknownValueError: # sometimes if the audio is empty this happens
			pass


print()
print("Total TTS parsed: {}".format(total))
print("Total Google got correct: {}/{}, or {}%".format(corrects["google"],total, round((corrects["google"]/total)*10000)/100))
print("Total Wit got correct: {}/{}, or {}%".format(corrects["wit"],total, round((corrects["wit"]/total)*10000)/100))