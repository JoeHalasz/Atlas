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



# this will return the start time and the end time if they exist in the string.
# it will also change the text so that it does not have the time and the time trigger
# word in the text 
def getTime(text):
	startTime = ""
	endTime = ""
	rest = ""
	text = text.replace(" at night", "pm")
	text = text.replace(" pm", "pm")
	text = text.replace(" am", "am")
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


def getDateWithDayMonth(day, month):
	dateTime = datetime.datetime.today().replace(day=int(day))
	dateTime = dateTime.replace(month=MONTHS.index(month.lower())+1)
	dateTime = formatDate(dateTime)
	return dateTime


def formatDate(wantedDate):
	return wantedDate.strftime('%m/%d/%y')


def getDaysFromToday(addDays):
	wantedDate = datetime.datetime.today() + datetime.timedelta(days=int(addDays))
	wantedDate = datetime.datetime.strptime(str(wantedDate).split(".")[0], '%Y-%m-%d %H:%M:%S')
	return formatDate(wantedDate)


def getDate(text):
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
	
	if not wantedDate:
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
			text = text[1:-1]
		if text[-1] == " ": # get rid of space at the end
			text = text[0:-2] 
		calendarAdd(text, wantedDate, startTime, endTime)
	except ValueError:
		print("Something about the entered date does not work.")
		print(traceback.format_exc())


