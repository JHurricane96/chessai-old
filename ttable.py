import config

# Used for ABnegamax
class ttableEntry:
	zobristHash = 0L
	scoreType = 0 #0 accurate; 1 lower bound; 2 upper bound
	score = 0
	bestMove = None
	finalBoardPos = None
	depth = 0 #From bottom
	result = ''

# Used for gamma negamax
"""class ttableEntry:
	zobristHash = 0L
	minScore = -config.MAX_SCORE
	maxScore = config.MAX_SCORE
	bestMove = None
	finalBoardPos = None # Only useful for learning to find features. 
	# TODO: implement separate trans-tables for learning and playing
	depth = 0 #From bottom
	result = ''"""

class ttable:
	table = {}
	size = 0
	maxSize = 10**8
	#debug info below
	hits = 0
	notHits = 0