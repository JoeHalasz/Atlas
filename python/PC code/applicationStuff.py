import subprocess
import win32gui
import time
from pynput.keyboard import Key


# helper function for get_app_list
def window_enum_handler(hwnd, resultList):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
        resultList.append((hwnd, win32gui.GetWindowText(hwnd)))


# this function will return all the open and visible windows
def get_app_list(handles=[]):
    mlst=[]
    win32gui.EnumWindows(window_enum_handler, handles)
    for handle in handles:
        mlst.append(handle)
    return mlst

# this fuction will bring a window to the forground
appwindows = get_app_list()
def bringToForground(name, keys, endFast=False):
	noneFound = True
	tries = 0
	while noneFound:
		allApps = reversed(get_app_list())
		for app in allApps:
			# print(app[1])
			if name in app[1].lower():
				noneFound = False
				keys.press(Key.alt) # next function only works if alt key is pressed
				try:
					win32gui.SetForegroundWindow(win32gui.FindWindow(None,app[1]))
				except:
					noneFound = True
				keys.release(Key.alt)
				break
		if tries > 20 and endFast:
			break
		tries += 1
		time.sleep(.02) # wait for program to open


# This function will open an application or create a new tab
# It will also attempt to bring that new window into the forground
# TODO better way to do this might be to press the windows key and type it then press enter
def openApplication(commandParams, keys):
	if "chrome" in commandParams:
		subprocess.Popen('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
		bringToForground("chrome", keys)
	elif "sublime" in commandParams:
		subprocess.Popen('C:\\Program Files\\Sublime Text 3\\sublime_text.exe')
		bringToForground("sublime", keys)
	elif "brave" in commandParams:
		subprocess.Popen('C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe')
		bringToForground("brave", keys)
	elif "git" in commandParams:
		subprocess.Popen('C:\\Users\\jhala\\AppData\\Local\\GitHubDesktop\\GitHubDesktop.exe')
		bringToForground("git", keys)
	elif "unity" in commandParams:
		subprocess.Popen('C:\\Program Files\\Unity Hub\\Unity Hub.exe')
		bringToForground("unity", keys)
	elif "new tab" in commandParams:
		keys.press(Key.ctrl_l)
		keys.press("t")
		keys.release(Key.ctrl_l)
		keys.release("t")
