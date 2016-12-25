import csv, sys
import copy
import math
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
		_invalid_args()

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

	metashare = {}
	for archetype in archetypes:
		# #10 means 10 decks, 12.5% means that much of the field
		metashare[archetype] = mudata[(archetype, archetype)]

	if verbose:
		_visualize_data(mudata, archetypes)

	_validate(mudata, archetypes, metashare)

	if verbose:
		print "\nGenerating deck counts from input"
	deckcounts = _generate_deck_counts(metashare, attendance)

	if verbose:
		print "\nCounts of decks by archetype"
		total = 0
		for key in deckcounts:
			total += deckcounts[key]
			print key + ':' + str(deckcounts[key])
		print total
	playerlist = _generate_players(deckcounts)
	print "{} players entered".format(len(playerlist))
	# if verbose:
	# 	print "\nGenerated players\nPlayer: Archetype"
	# 	for player in playerlist.playerlist:
	# 		print "{}: {}".format(player.id, player.archetype)

	#Write a method to simulate a round now
	#Should I just be using a DB backend?
	rounds = int(math.ceil(math.log(len(playerlist), 2)))
	print rounds

	for round_num in xrange(rounds):
		print "\nRound #{}".format(round_num+1)
		pairings = playerlist.generate_pairings()

		# if verbose:
		# 	for pair in pairings:
		# 		print "{} vs {}".format(pair[0].id, pair[1].id)

		results = playerlist.process_pairings(pairings, mudata)



	standings = playerlist.generate_standings()
	_print_standings(standings)

class Player(object):
	'''
	Object to represent a player
	'''
	playercount = 0
	def __init__(self, archetype):
		self.id = Player.playercount
		Player.playercount += 1
		self.archetype = archetype
		self.wins = 0
		self.losses = 0
		self.draws = 0
		self.points = 0
		self.opponentids = []
		self.owm = 0
		#Tiebreakers?

	def defeats(self, opponent):
		self.wins += 1
		self.points += 3
		self.opponentids.append(opponent.id)
		opponent.losses += 1
		opponent.opponentids.append(self.id)

	def calculate_omw(self, playerlist):
		oppwins = 0
		opplosses = 0
		for id in self.opponentids:
			oppwins += playerlist[id].wins
			opplosses += playerlist[id].losses
		self.omw = float(oppwins) / float(oppwins+opplosses)
		return self.omw

	def calculate_ogw():
		#This is actually hard to simulate given MW%
		pass

class PlayerList(object):
	'''
	Object to represent all attendees with helper functions as well
	'''

	def __init__(self, playerlist):
		self.playerlist = copy.copy(playerlist)
		self.pointsmap = {0: copy.copy(playerlist)}

	def regen_pointsmap(self):
		'''
		Regenerate the pointsmap from the current playerlist
		'''
		self.pointsmap = {}
		for player in self.playerlist:
			try:
				self.pointsmap[player.points].append(player)
			except KeyError:
				self.pointsmap[player.points] = [player]

	def get_players_with_points(points):
		return self.pointsmap[points]

	def generate_standings(self):
		self.regen_pointsmap()
		standings = []
		for pointtotal in self.pointsmap.keys()[::-1]:
			print "Adding points of {}: {} players".format(pointtotal, len(self.pointsmap[pointtotal]))
			standings.extend(sorted(self.pointsmap[pointtotal], key=lambda x: x.calculate_omw(self.playerlist), reverse=True))
			print "ID: {}".format(standings[-1].id)
		return standings

	def generate_pairings(self):
		pairings = []
		paireddownplayer = ""
		self.regen_pointsmap()
		for pointtotal in self.pointsmap.keys()[::-1]:		#Pair players by high points first
			playerpool = copy.copy(self.pointsmap[pointtotal])
			random.shuffle(playerpool)
			if paireddownplayer != "":
				pairedupplayer = playerpool.pop()
				pairings.append((pairedupplayer, paireddownplayer))
				paireddownplayer = ""
				#TODO mulligan if they've played before to increase accuracy

			while len(playerpool) > 1:
				p1 = playerpool.pop()
				p2 = playerpool.pop()
				pairings.append([p1, p2])

			if len(playerpool) == 1:
				paireddownplayer = playerpool.pop()

		if paireddownplayer != "":
			#TODO Implement BYE instead of dropping
			print "Dropped player {}".format(paireddownplayer.id)

		return pairings

	def process_pairings(self, pairings, mudata):
		points_earned = {0:[], 1:[], 3:[]}
		for pairing in pairings:
			wpct = mudata[(pairing[0].archetype, pairing[1].archetype)]
			p1_id = pairing[0].id
			p2_id = pairing[1].id

			if random.random() <= wpct:
				self.playerlist[p1_id].defeats(self.playerlist[p2_id])
				points_earned[3].append(pairing[0])	#winner
				points_earned[0].append(pairing[1]) #loser
			else:
				self.playerlist[p2_id].defeats(self.playerlist[p1_id])
				points_earned[3].append(pairing[1])	#winner
				points_earned[0].append(pairing[0]) #loser
		return points_earned

	def __len__(self):
		return len(self.playerlist)

def _generate_players(deckcounts):
	playerlist = []
	for key in deckcounts:
		for x in xrange(deckcounts[key]):
			playerlist.append(Player(key))
	return PlayerList(playerlist)

def _generate_deck_counts(metashare, attendance):
	meta_dict = {}
	totalpct = 0
	undecidedplayers = int(attendance)
	print "{} undecided players".format(undecidedplayers)
	weighted_pairs = []
	# Assign the static counts of players first
	for archetype in metashare:
		print "Assigning archetype {}".format(archetype)
		weight = metashare[archetype]
		if weight[0] == '#':
			meta_dict[archetype] = int(weight[1:])
			undecidedplayers = undecidedplayers - int(weight[1:])
		else:
			meta_dict[archetype] = 0
			totalpct += float(weight[:-1])
			weighted_pairs.append((archetype, totalpct))

	print "{} undecided players about to be given weighted decks".format(undecidedplayers)
	for x in xrange(undecidedplayers):
		r = random.random() * 100

		'''
		Meta distribution brackets looks like this (weighted_pairs)
		('Miracles', 14.22)
		('Lands', 18.01)
		('Chaff', 48.34)
		('Grixis Delver', 55.92)
		('UR Delver', 59.71)
		('Maverick', 62.08)
		('BUG Delver', 65.39999999999999)
		('Burn', 68.71999999999998)
		('Eldrazi', 77.24999999999999)
		('Storm', 83.40999999999998)
		('Aluren', 85.77999999999999)
		('Shardless BUG', 91.46999999999998)
		('Death and Taxes', 93.83999999999999)
		('4c Loam', 96.21)
		('Sneak and Show', 100.0)
		'''

		#Cascade through dict to find the correct bracket the value belongs in
		for archetype, ceil in weighted_pairs:
			if ceil > r:
				meta_dict[archetype] = meta_dict[archetype] + 1
				break
	return meta_dict

def _validate(mudata, archetypes, metashare):
	totalregex = re.compile('^#\d+$') #Regex for a specific number of decks
	pctregex = re.compile('^\d{1,2}(\.\d\d)?%$') #Regex for 
	for key in metashare:
		amount = metashare[key]
		if not (totalregex.match(amount) or pctregex.match(amount)):
			raise ValueError("Invalid meta share units: {0}".format(amount))

	if len(set(archetypes)) != len(archetypes):
		raise ValueError("Duplicate archetypes given")

def _visualize_data(data, archetypes):
	print "\nMatchup grid"
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

def _print_standings(standings):
	print "\nStandings:"
	print "Place\t|Points\t|OMW\t\t|Archetype"
	for index, player in enumerate(standings):
		print "{}:\t{}\t{}\t{} (#{})".format(index+1, player.points, player.omw, player.archetype, player.id)

def _invalid_args():
	print "Usage: SwissSim <fileName>"
	exit(0)

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		_invalid_args
	else:
		main(sys.argv[1:])