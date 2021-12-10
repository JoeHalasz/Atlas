from forPC import *

run_event = threading.Event()
run_event.set()
t = threading.Thread(target=Events.createTimedEvents, args=(run_event,))
t.start()

try:
	while True:
		textTransform(input())
except KeyboardInterrupt as e:
	pass
except Exception as e:
	print(e)
	print("Other error")
print("Stopping event thread")
run_event.clear()

t.join()