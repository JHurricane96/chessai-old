"""class ttableEntry:
	zobristHash = 0L
	scoreType = 0 #0 accurate; 1 lower bound; 2 upper bound
	score = 0
	bestMove = None
	depth = 0 #From bottom
	result = ''"""
MAX_SCORE = 10000

class ttableEntry:
	zobristHash = 0L
	minScore = -(MAX_SCORE)
	maxScore = MAX_SCORE
	bestMove = None
	finalBoardPos = None
	depth = 0 #From bottom
	result = ''""

class ttable:
	table = {}
	size = 0
	maxSize = 10**8
	#debug info below
	hits = 0
	notHits = 0