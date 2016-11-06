import sys
import random



def main(argv):
	#Parse data
	try:
		gwpct = float(argv[0])
		total = int(argv[1])
	except IndexError:
		invalid_args()
	
	results = {"2-0": 0, "2-1": 0, "1-2": 0, "0-2": 0}
	
	for x in xrange(total):
		wins = 0
		losses = 0
		for x in xrange(3):
			if wins != 2 and losses != 2:
				if (random.random()<gwpct):
					wins += 1
				else:
					losses += 1

		results[str(wins)+"-"+str(losses)] += 1

	for key in results:
		print "{0}: {1}".format(key, results[key])

	mwpct = float(results["2-0"] + results["2-1"])/float(results["1-2"] + results["0-2"] + results["2-0"] + results["2-1"])
	print "MW%: {0}".format(mwpct)

def invalid_args():
	print "Usage: GwMwConverter.py <gw pct> <matches>"
	exit(0)

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		show_usage()
	else:
		main(sys.argv[1:])