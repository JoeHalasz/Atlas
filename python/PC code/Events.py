import time
import EventClasses

eventChanges = []


def checkTimedEvents(events):
	# check all the timed events
	for event in events:
		event.refresh()



def createTimedEvents(run_event): # this is a thread	
	global eventChanges
	startTime = time.time()
	# this should be a list of pairs where [0] is the name and [1] is the time it should starts
	events = [EventClasses.Calendar()] 
	
	while run_event.is_set():
		checkTimedEvents(events)
		if (len(eventChanges) != 0):
			for eventChange in eventChanges:
				for event in events:
					if (event.name == eventChange.name):
						# this is the event that has a change
						print("here")
						event.makeChange(eventChange)
			eventChanges = []



