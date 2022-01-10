import time
from Google import Create_Service, convert_to_RFC_datetime
import traceback

class EventChange():
	#				        action(add), thing to add
	def __init__(self, name, changeType, changes):
		self.name = name
		self.changeType = changeType
		self.changes = changes


class Event():

	# pass in the name of the event and the amount of seconds it should wait until the next refresh
	def __init__(self, name="event", refreshTime=1):
		self.name = name
		self.refreshTime = refreshTime
		self.nextRefresh = refreshTime + time.time()

	def refresh(self):
		currentTime = time.time()
		if (currentTime > self.nextRefresh):
			self.nextRefresh += self.refreshTime
			return True
		return False



class Calendar(Event):

	# here is the Google Calendar API
	# https://developers.google.com/calendar/api/v3/reference/events/get#examples
	

	events = []
	

	# create a calendar item
	# creates an API connection with Google calendar 
	# gets all the events currently in the calendar
	def __init__(self):
		super().__init__("calendar", 60) # this means that every 60 seconds it will be refreshed
		API_NAME = 'calendar'
		API_VERSION = 'v3'
		SCOPES = ['https://www.googleapis.com/auth/calendar']
		CLIENT_FILE = 'CalendarAddress.json'
		self.service = Create_Service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)
		self.refresh(True) # force it to refresh the first time 
		# self.printCalendarItems()
		

	# will print all the current events in self.events
	def printCalendarItems(self):
		print("Here are all the things in the calendar:")
		for event in self.events:
			print("  " + event['summary'])
			for key, value in event.items():
				print("    " + key, ' : ', value)
		

	# will attempt to delete the calendar item with the name eventName
	# will return true or false depending on if it could find that event or not
	def deleteCalendarItem(self, eventName, eventDate):
		found = False
		if eventName == "all events" and eventDate == None:
			return False # do not allow user to delete all events on the calendar without a given date
		for event in self.events:
			nameCorrect = False
			dateCorrect = False
			if (event['summary'] == eventName or eventName == "all events"):
				nameCorrect = True
			if eventDate == None:
				dateCorrect = True
			else:
				date = event['start']
				try:
					date = date['date']
				except:
					date = date['dateTime']
					date = date.split("T")[0] # remove the time part
				date = date.split("-")
				date = date[1]+"/"+date[2]+"/"+date[0][-2:]
				if eventDate == date:
					dateCorrect = True

			if nameCorrect and dateCorrect:
				try:
					self.service.events().delete(calendarId='primary', eventId=event['id']).execute()
				except:
					if "Resource has been deleted" in traceback.format_exc():
						pass # this means that that thing already got deleted a little bit ago
					else:
						print(traceback.format_exc())
				found = True
				if eventName != "all events": # this will allow remove all to work
					break
		if not found:
			if eventDate != None:
				print('Could not find event: "{}" on {}'.format(eventName, eventDate))
			else:
				print('Could not find event: "{}"', eventName)

		return found

	def addCalendarItem(self,name,date,startTime="8am", endTime=""):
		text = '{} {} {}'.format(name, date,startTime)
		if endTime != "":
			text+="-"+endTime
		newEvent = self.service.events().quickAdd(
		    calendarId='primary',
		    text=text.format(date,time)).execute()
	

	# will refresh the self.events list
	def refresh(self, forceRefresh=False):
		if (forceRefresh or super().refresh()):
			page_token = None
			events = []
			while True:
				newEvents = self.service.events().list(calendarId='primary', pageToken=page_token).execute()
				for event in newEvents['items']:
					events.append(event)
				page_token = newEvents.get('nextPageToken')
				if not page_token:
					break
			self.events = events
	

	# a calendar EventChange will be formated like this:
	# name = name
	# changeType = "add";"remove"
	# change = [name, date(optional), time(optional)]
	def makeChange(self, change):
		self.refresh(True) 
		name = change.changes[0]
		date = change.changes[1]
		if (change.changeType == "add"):
			startTime = change.changes[2][0]
			endTime = change.changes[2][1]
			print('Adding "{}" to your schedule {} {}{}'.format(name, date,startTime,"-"+endTime))
			self.addCalendarItem(name, date,startTime,endTime)
		elif (change.changeType == "remove"):
			print('Attempting to remove "{}" from your schedule on {}.'.format(name, date))
			self.deleteCalendarItem(name, date)
		else:
			print("Unknown changeType for Calendar: {}".format(change.changeType))

