import Events
import EventClasses
import datetime
import traceback


MONTHS = ["january","february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]



# name,date,starttime,endtime
def calendarAdd(name,date,startTime="8am",endTime=""):
	Events.eventChanges.append(EventClasses.EventChange("calendar", "add", [name, date, [startTime, endTime]]))
	
	

def calendarRemove(name):
	Events.eventChanges.append(EventClasses.EventChange("calendar", "remove", [name]))


def addDays(addDays):
	wantedDate = datetime.datetime.today() + datetime.timedelta(days=int(addDays))
	wantedDate = datetime.datetime.strptime(str(wantedDate).split(".")[0], '%Y-%m-%d %H:%M:%S')
	return formatDate(wantedDate)


def formatDate(wantedDate):
	return wantedDate.strftime('%m/%d/%y')


def checkTime(name, text, wantedDate): # TODO add from time1 to time2
	print(name)
	if type(wantedDate) != str:
		wantedDate = formatDate(wantedDate)
	split = wantedDate.split("/")
	day = int(split[1])
	month = int(split[0])
	year = 2000+int(split[2])
	checkWantedDate = datetime.datetime(year,month,day)
	if checkWantedDate < datetime.datetime.today():
		month += 1
		if month > 12:
			month-=12
			year += 1
		wantedDate = formatDate(datetime.datetime(year,month, day))
	split = text.split(" at ")
	if len(split) > 1: # this means there was an "at" and the user specified a time
		time = "at "+ split[1]
		calendarAdd(name, wantedDate, time)
		return
	split = text.split(" from ")
	if len(split) > 1: # same as above except it has a start and end time after "from"
		split2 = split[1].split(" to ")
		beforeTime = split2[0]
		afterTime = split2[1]
		print()
		print(beforeTime)
		calendarAdd(name, wantedDate, beforeTime, afterTime)
		return
	
	calendarAdd(name, wantedDate)



# when there is day or days in the text
def dayParsing(text):
	if "day" in text: # day and days is the same because we are taking the first part of the split
		split = text.split("day")
		addDays = split[0]
		wantedDate = getDate(addDays)
		
		wantedDate = str(wantedDate) # add "on" to it 
		return wantedDate
	else:
		print("Not sure what to do with this command:")
		print(text)
		return None


def getDateWithDayFirst(text):
	# This will be formatted like "5th of december at..." or "5th at..."
	if " at" in text:
		text = text.split(" at")[0]
	else:
		text = text.split(" from")[0]
	split = text.split(" ")

	day = split[0].replace("st","").replace("nd","").replace("rd","").replace("th","") # make 1st into 1
	if len(split) == 1:
		return datetime.datetime.today().replace(day=int(day))
	month = split[2]
	return getDateWithDayMonth(day, month)

	# TODO make this return the date it should be 

	

def getDateWithMonthFirst(text):
	# This will be formatted like "December 5th at..."
	pieces = text.split(" ")
	month = pieces[0] # the next word should be the month
	day = pieces[1].replace("st","").replace("nd","").replace("rd","").replace("th","") # make 1st into 1
	return getDateWithDayMonth(day,month)
	# TODO get the date based off of the month and the day and return it

def getDateWithDayMonth(day, month):
	dateTime = datetime.datetime.today().replace(day=int(day))
	dateTime = dateTime.replace(month=MONTHS.index(month.lower()))
	return dateTime




# this function assumes that the command has been taken out and then name of the thing 
# to add the the schedule is the first thing in the string.
# this means it can be used for any commands that fit that format.
# the exampe one is "remind me to" but this could also be something like
# "I have to" 
def remindMeToParsing2(textWithCommand, command):
	# TODO change this to always get the text right after "at" or "from" as the time
	# TODO change this to always get the date right after "on" as the date
	# TODO change this to always get the name as what ever is left after removing "to", "from", "on", and the time and date
	try:
		text = textWithCommand.replace(command+" ", "")
		# remind me to [name] in 2 days at ____
		split = text.split(" in ", 1) # this will split at the last one 
		if (len(split) > 1): # that means the word "in" splits the name and when to add it
			name = split[0]
			rest = split[1]
			wantedDate = dayParsing(rest)
			if wantedDate:
				checkTime(name, text, wantedDate) # this will also set it in the calendar
			return 
		# remind me to [name] on the 5th
		# remind me to [name] on the 5th of december
		split = text.split(" on the ", 1) # this will split at the last one 
		if (len(split) > 1):
			name = split[0]
			rest = split[1]
			wantedDate = getDateWithDayFirst(rest)
			if wantedDate:
				checkTime(name, text, wantedDate) # this will also set it in the calendar
			return

		# remind me to [name] on december 4th at 5pm
		split = text.split(" on ", 1) # this will split at the last one 
		if (len(split) > 1):
			name = split[0]
			rest = split[1]
			wantedDate = getDateWithMonthFirst(rest)
			checkTime(name,text,wantedDate)
			return
		elif "tomorrow" in text:
			split = text.split(" tomorrow",1)
			wantedDate = getDate(1) # get tomorrows date
			checkTime(split[0],split[1], wantedDate)
			return
		elif "today" in text:
			split = text.split(" today",1)
			wantedDate = getDate(0)
			checkTime(split[0],split[1], wantedDate)
			return			



		for month in MONTHS:
			split = text.split(month,1)
			if len(split) > 1:
				name = split[0]
				rest = text.replace(name,"")
				wantedDate = getDateWithMonthFirst(rest)
				checkTime(name, text, wantedDate)


	except ValueError:
		print("Something about the entered date does not work.")
		print(traceback.format_exc())


		# todo finish this
	# TODO any other formats



# ---------------------------------- NEW VERSION --------------------------------------------

# this will return the start time and the end time if they exist in the string.
# it will also change the text so that it does not have the time and the time trigger
# word in the text 
def getTime(text):
	startTime = ""
	endTime = ""
	rest = ""
	text.replace(" at night", "pm")
	text.replace(" pm", "pm")
	text.replace(" am", "am")
	if "at " in text: # there is an "at" in the text somewhere
		split = text.split(" ")
		x = 0
		while x < len(split):
			if split[x] == "at":
				startTime = split[x+1]
				if not "pm" in startTime and not "am" in startTime:
					if "tonight" in text or "tomorrow night" in text:
						startTime += "pm"
				x += 1 # skip the next part with the number in it
			else:
				rest += split[x] + " "
			x+=1
		text = rest
	elif "from " in text: # there is a "from" in the text somewhere
		split = text.split(" ")
		x = 0
		while x < len(split):
			if split[x] == "from":
				startTime = split[x+1]
				endTime = split[x+3]
				if not "pm" in startTime and not "am" in startTime:
					if "tonight" in text or "tomorrow night" in text:
						startTime += "pm"
						endTime += "pm"
				x += 3 # skip the next part with the number in it
			else:
				rest += split[x] + " "
			x+=1
		text = rest
	return text, startTime, endTime


def getDaysFromToday(addDays):
	wantedDate = datetime.datetime.today() + datetime.timedelta(days=int(addDays))
	wantedDate = datetime.datetime.strptime(str(wantedDate).split(".")[0], '%Y-%m-%d %H:%M:%S')
	return formatDate(wantedDate)


def getDate(text):
	rest = ""
	wantedDate = ""
	if "tomorrow" in text:
		wantedDate = getDaysFromToday(1)
		text = text.replace("tomorrow night", "")
		text = text.replace("tomorrow", "")
	elif "today" in text or "tonight" in text:
		wantedDate = getDaysFromToday(0)
		text = text.replace("today", "")
		text = text.replace("tonight","")
	else:
		
		if "day" in text:
			split = text.split(" ")
			x = 0
			while x < len(split):
				if split[x] == "in":
					addDays = split[x+1]
					wantedDate = getDaysFromToday(addDays)
					x += 2
				else:
					rest += split[x] + " "
				x += 1
			text = rest
		elif "week" in text 

	return text, wantedDate



def remindMeToParsing(text, command):
	
	# TODO change this to always get the text right after "at" or "from" as the time
	# TODO change this to always get the date right after "on" as the date
	# TODO change this to always get the name as what ever is left after removing "to", "from", "on", and the time and date
	
	text, startTime, endTime = getTime(text)
	# there will not be any time stuff in text anymore 
	text, wantedDate = getDate(text)
	text = text.replace(command.lower() + " ","")
	if text[0] == " ":
		text = text[1:-1]
	print(wantedDate)
	print(startTime, endTime)
	print(text)


