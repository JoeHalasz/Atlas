from forPC import *
import traceback


run_event = threading.Event()
run_event.set()
t = threading.Thread(target=Events.createTimedEvents, args=(run_event,1))
t.start()

try:
	while True:
		textTransform(input())
except KeyboardInterrupt as e:
	pass
except:
	print(traceback.format_exc())
	print("Other error")
print("Stopping event thread")
run_event.clear()

t.join()