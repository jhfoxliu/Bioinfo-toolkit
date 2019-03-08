import sys,time
from time import gmtime, strftime

if not sys.argv[1]:
	sys.stderr.write("Please provide a interval to sleep.\n")
else:
	if sys.argv[1].endswith("h"):
		interval = sys.argv[1].strip("h")
		interval = int(interval) * 3600
	elif sys.argv[1].endswith("hr"):
		interval = sys.argv[1].strip("hr")
		interval = int(interval) * 3600
	elif sys.argv[1].endswith("min"):
		interval = sys.argv[1].strip("min")
		interval = int(interval) * 60
	elif sys.argv[1].endswith("s") or sys.argv[1].endswith("sec"):
		interval = sys.argv[1].strip("s")
		interval = int(interval)
	else:
		interval = sys.argv[1]
		try:
			interval = int(interval)
		except ValueError:
			raise ValueError("Please provide a validated interval\n.")
		except TypeError:
			raise ValueError("Please provide a validated interval.\n")
	sys.stderr.write("Wait for %s seconds\n" % interval)
	time.sleep(interval)
	sys.stderr.write("Awake at %s\n" % strftime("%Y-%m-%d %H:%M:%S", time.localtime()))