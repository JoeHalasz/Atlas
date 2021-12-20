from os.path import exists



# this function should be called when a connection to a new PI is made for the first time
# it will return what that PI's id should be set to
def firstTimeConnection():
	if not exists("ids.txt"):
		with open("ids.txt", "w") as f:
			f.write("1\n")
		return 1
	else:
		nums = []
		with open("ids.txt", "r") as f:
			lines = f.readlines()
			for line in lines:
				nums.append(int(line))

		with open("ids.txt", "a") as f:
			f.write(str(len(nums)+1) + "\n")

		return len(nums)+1
			
