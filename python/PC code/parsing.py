import Events
import EventClasses
import datetime
import traceback


MONTHS = ["january","february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]



# name,date,starttime,endtime
def calendarAdd(name,date,startTime="8am",endTime=""):
	Events.eventChanges.append(EventClasses.EventChange("calendar", "add", [name, date, [startTime, endTime]]))
	
	

def calendarRemove(name, date):
	Events.eventChanges.append(EventClasses.EventChange("calendar", "remove", [name, date]))



# this will return the start time and the end time if they exist in the string.
# it will also change the text so that it does not have the time and the time trigger
# word in the text 
def getTime(text):
	startTime = ""
	endTime = ""
	rest = ""
	text = text.replace(" at night", "pm")
	text = text.replace(" pm", "pm")
	text = text.replace(" p.m.", "pm")
	text = text.replace(" am", "am")
	text = text.replace(" a.m.", "am")
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
			if split[x] == "from" and len(split) > x+3:
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


def getDateWithDayMonth(day, month):
	dateTime = datetime.datetime.today().replace(day=int(day))
	if month:
		dateTime = dateTime.replace(month=MONTHS.index(month.lower())+1)
	dateTime = formatDate(dateTime)
	return dateTime


def formatDate(wantedDate):
	return wantedDate.strftime('%m/%d/%y')


def getDaysFromToday(addDays):
	wantedDate = datetime.datetime.today() + datetime.timedelta(days=int(addDays))
	wantedDate = datetime.datetime.strptime(str(wantedDate).split(".")[0], '%Y-%m-%d %H:%M:%S')
	return formatDate(wantedDate)


def getDaysFromDate(date, addDays):
	date = date.split("/")
	date = datetime.datetime.today().replace(day=int(date[1]),month=int(date[0]),year=2000+int(date[2]))
	wantedDate = date + datetime.timedelta(days=int(addDays))
	wantedDate = datetime.datetime.strptime(str(wantedDate).split(".")[0], '%Y-%m-%d %H:%M:%S')
	return formatDate(wantedDate)


def getDate(text, needDate=True):
	rest = ""
	wantedDate = None
	if "tomorrow" in text:
		wantedDate = getDaysFromToday(1)
		text = text.replace("tomorrow night", "")
		text = text.replace("tomorrow", "")
	elif "today" in text or "tonight" in text:
		wantedDate = getDaysFromToday(0)
		text = text.replace("today", "")
		text = text.replace("tonight","")
	elif "day" in text:
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
	else:
		for month in MONTHS: # this could be i have to do homework december 5th or the 5th of december
			if month in text:
				split = text.split(" ")
				x = 0
				while x < len(split):
					if split[x] == month:
						if x != 0 and split[x-1] == "of": # it is formatted like 5th of december
							day = split[x-2]
							month = split[x]
							text = text.replace("on the " + day + " of " + month, "")
							text = text.replace("the " + day + " of " + month, "")
							text = text.replace(day + " of " + month, "")
							day = day.replace("st","").replace("nd","").replace("rd","").replace("th","") # make 1st into 1
							wantedDate = getDateWithDayMonth(day,month)
							break
						else: # it is formatted like december 5th
							day = split[x+1]
							month = split[x]
							text = text.replace("on " + month + " " + day, "")
							text = text.replace(month + " " + day, "")
							day = day.replace("st","").replace("nd","").replace("rd","").replace("th","") # make 1st into 1
							wantedDate = getDateWithDayMonth(day,month)
							break
					x += 1
				break
		if wantedDate == None:
			if "on the" in text:
				try:
					day = text.split("on the ")[1].split(" ")[0]
					text = text.replace("on the " + day, "")
					day = day.replace("st","").replace("nd","").replace("rd","").replace("th","") # make 1st into 1
					wantedDate = getDateWithDayMonth(day, None)
				except:
					pass
	
	if not wantedDate and needDate:
		wantedDate = getDaysFromToday(0) # if there is no date then use today

	return text, wantedDate


# this function assumes that the command has been taken out and then name of the thing 
# to add the the schedule is the first thing in the string.
# this means it can be used for any commands that fit that format.
# the exampe one is "remind me to" but this could also be something like
# "I have to" 
def remindMeToParsing(text, command):
	try:		
		text, startTime, endTime = getTime(text)
		# there will not be any time stuff in text anymore 
		text, wantedDate = getDate(text)
		text = text.replace(command.lower() + " ","")
		if text[0] == " ": # get rid of space at beggining
			text = text[1:]
		if text[-1] == " ": # get rid of space at the end
			text = text[0:-1] 
		calendarAdd(text, wantedDate, startTime, endTime)
		calendarAdd("Remember to " + text + " tomorrow", getDaysFromDate(wantedDate, -1), startTime, endTime)
	except ValueError:
		print("Something about the entered date does not work.")
		print(traceback.format_exc())


def removeFromScheduleParsing(text, command):
	firstWord = text.split(" ")[0] 
	if firstWord == "remove" or firstWord == "delete":
		text = ' '.join(text.split()[1:]) # delete first word
	# there will not be any time stuff in text anymore 
	text, wantedDate = getDate(text, False)
	text = text.replace(command.lower() + " ","") 
	text = text.replace(command.lower(), "") 
	if text[0] == " ": # get rid of space at beggining
		text = text[1:]
	if text[-1] == " ": # get rid of space at the end
		text = text[0:-1] 
	calendarRemove(text, wantedDate)
