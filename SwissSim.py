import csv, sys

#Given the percent of people playing R, P, or S generate a simulated bracket
#Expand into being a MTG Metagame simulator?
#IDs seems hard to simulate.
#Have an option for a Day 2 cut and sim again?
#Have an option for a T8 cut and sim again?
def main(argv):
	#Parse data
	try:
		filename = argv[0]
	except IndexError:
		invalid_args()

	datafile = open(filename, 'r')
	datareader = csv.reader(datafile,delimiter=',')
	data = []
	for row in datareader:
		data.append(row)
		if len(data) == 1:
			archetypes = data[0][1:]
		else:
			assert row[0] in archetypes

	mudata = {}
	offset = 1
	for rowindex in xrange(1, len(data)):
		for columnindex in xrange(1, len(data)):
			activeplayer = data[rowindex][0]
			passiveplayer = data[0][columnindex]
			mudata[(activeplayer, passiveplayer)] = data[rowindex][columnindex]

			print activeplayer + " vs " + passiveplayer + ": " + data[rowindex][columnindex]

	metashare = {}
	for archetype in archetypes:
		metashare[archetype] = mudata[(archetype, archetype)]

	visualize_data(mudata, archetypes)

def validate(filename):
	with open(fileName, 'r') as f:

		for line in f:
			print "..."

def visualize_data(data, archetypes):
	header = "\t"
	for archetype in archetypes:
		header += archetype[:7] + "\t"
	print header

	for activeplayer in archetypes:
		line = activeplayer[:7] + "\t"
		for passiveplayer in archetypes:
			text = data[(activeplayer, passiveplayer)]
			line += text + "\t"
		print line

def invalid_args():
	print "Usage: SwissSim <fileName>"

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		show_usage()
	else:
		main(sys.argv[1:])