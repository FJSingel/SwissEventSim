import csv, sys
import re
import random

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

	verbose = True
	datafile = open(filename, 'r')
	datareader = csv.reader(datafile,delimiter=',')
	data = []
	for row in datareader:
		data.append(row)
		if len(data) == 1:
			archetypes = data[0][1:]
			attendance = data[0][0]
		else:
			assert row[0] in archetypes

	mudata = {}
	offset = 1
	for rowindex in xrange(1, len(data)):
		for columnindex in xrange(1, len(data)):
			activeplayer = data[rowindex][0]
			passiveplayer = data[0][columnindex]

			if rowindex == columnindex:
				if activeplayer != passiveplayer:
					raise ValueError("Axes do not match")
				value = data[rowindex][columnindex]
			else:
				value = int(data[rowindex][columnindex])
			mudata[(activeplayer, passiveplayer)] = value

			print activeplayer + " vs " + passiveplayer + ": " + data[rowindex][columnindex]

	metashare = {}
	for archetype in archetypes:
		# #10 means 10 decks, 12.5% means that much of the field
		metashare[archetype] = mudata[(archetype, archetype)]

	if verbose:
		visualize_data(mudata, archetypes)
	validate(mudata, archetypes, metashare)

	deckcounts = generate_deck_counts(metashare, attendance)

	if verbose:
		for key in deckcounts:
			print key + ':' + str(deckcounts[key])


def generate_deck_counts(metashare, attendance):
	meta_dict = {}
	totalpct = 0
	undecidedplayers = int(attendance)
	weighted_pairs = []
	for archetype in metashare:
		weight = metashare[archetype]
		if weight[0] == '#':
			meta_dict[archetype] = int(weight[1:])
			undecidedplayers = undecidedplayers - int(weight[1:])
		else:
			meta_dict[archetype] = 0
			totalpct += float(weight[:-1])
			weighted_pairs.append((archetype, totalpct))

	for x in xrange(undecidedplayers):
		r = random.random() * undecidedplayers
		for archetype, ceil in weighted_pairs:
			if ceil > r:
				meta_dict[archetype] = meta_dict[archetype] + 1
				break

	for key in weighted_pairs:
		print key

	return meta_dict

def validate(mudata, archetypes, metashare):
	totalregex = re.compile('^#\d+$') #Regex for a specific number of decks
	pctregex = re.compile('^\d{1,2}(\.\d\d)?%$') #Regex for 
	for key in metashare:
		amount = metashare[key]
		if not (totalregex.match(amount) or pctregex.match(amount)):
			raise ValueError("Invalid meta share units: {0}".format(amount))

	if len(set(archetypes)) != len(archetypes):
		raise ValueError("Duplicate archetypes given")

def visualize_data(data, archetypes):
	header = "\t"
	for archetype in archetypes:
		header += archetype[:7] + "\t"
	print header

	for activeplayer in archetypes:
		line = activeplayer[:7] + "\t"
		for passiveplayer in archetypes:
			text = str(data[(activeplayer, passiveplayer)])
			line += text + "\t"
		print line

def invalid_args():
	print "Usage: SwissSim <fileName>"

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		show_usage()
	else:
		main(sys.argv[1:])