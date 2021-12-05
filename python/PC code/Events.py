import time



# this should be a list of pairs where [0] is the name and [1] is the time it should start
startTime = time.time()
eventTriggers = [
				["refresh calender", startTime]] 



def refreshCalendar():
	# TODO refresh the google calendar
	pass


# maybe dont use a thread because it doesnt matter on this end and just have the classes come with the events





# this is what gets called to actually do an event
# returns the next time the event should be triggered
def checkEventTriggers(event):
	name = event[0]

	if (name == "refresh calender"):
		refreshCalendar()
		return time.time() + 60 # update once per minute
	else:
		print("No event trigger for event: '" + event + "'")
		return time.time()


def createTimedEvents(run_event): # this is a thread
		# create all the timed stuff
		while run_event.is_set():
			# check all the timed events
			for x in range(len(eventTriggers)):
				event = eventTriggers[x]
				if (time.time() > event[1]):
					nextTrigger = checkEventTriggers(event) 
					eventTriggers[x][1] = nextTrigger # update the next update

	

