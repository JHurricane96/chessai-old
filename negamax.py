import chess
import evaluator
import ttable
import config

def ABnegamax(board, maxDepth, depth, alpha, beta, transTable):
	alphaOriginal = alpha

	zhash = board.zobrist_hash()
	entry = transTable.table.get(zhash)
	if entry and entry.depth >= maxDepth - depth:
		if entry.scoreType == 0: #exact value
			transTable.hits = transTable.hits + 1
			return (entry.move, entry.score)
		elif entry.scoreType == 1: #lower bound value
			alpha = max(alpha, entry.score)
		else: #upper bound value
			beta = min(beta, entry.score)
		if alpha >= beta:
			return (entry.move, entry.score)

	newEntry = False
	if not entry:
		entry = ttable.ttableEntry()
		entry.zobristHash = zhash
		newEntry = True
		entry.result = board.result()
	entry.depth = maxDepth - depth
	entry.move = ''

	#result = board.result()
	if (depth == maxDepth or entry.result != "*"):
		entry.score = evaluator.evaluator(board, entry.result)
		entry.finalBoardPos = board.fen()
		if (transTable.size == transTable.maxSize and newEntry):
			transTable.table.popitem()
			transTable.size = transTable.size - 1
		transTable.table[entry.zobristHash] = entry
		transTable.size = transTable.size + 1
		return ('', entry.score)

	maxScore = -(1<<128)
	score = maxScore
	bestMove = None

	for move in board.legal_moves:
		board.push(move)
		score = -ABnegamax(board, maxDepth, depth + 1, -beta, -alpha, transTable)[1]
		board.pop()

		if score > maxScore:
			maxScore = score
			bestMove = move

		alpha = max(alpha, score)
		if alpha >= beta:
			break

	entry.score = maxScore
	entry.move = bestMove
	if maxScore <= alphaOriginal:
		entry.scoreType = 2 #upper bound
	elif maxScore >= beta:
		entry.scoreType = 1 #lower bound
	else:
		entry.scoreType = 0 #exact
	if (transTable.size == transTable.maxSize and newEntry):
		transTable.table.popitem()
		transTable.size = transTable.size - 1
	board.push(bestMove)
	entry.finalBoardPos = transTable.table[board.zobrist_hash()].finalBoardPos
	board.pop()
	transTable.table[entry.zobristHash] = entry
	transTable.size = transTable.size + 1
	return (bestMove, maxScore)

def negamax(board, maxDepth, depth, gamma, transTable):
	zhash = board.zobrist_hash()
	entry = transTable.table.get(zhash)
	if entry and entry.depth >= maxDepth - depth:
		if entry.minScore > gamma:
			transTable.hits = transTable.hits + 1
			return (entry.bestMove, entry.minScore)
		elif entry.maxScore < gamma:
			transTable.hits = transTable.hits + 1
			return (entry.bestMove, entry.maxScore)
	
	newEntry = False
	if not entry:
		newEntry = True
		entry = ttable.ttableEntry()
		entry.zobristHash = zhash
		entry.result = board.result()
	entry.depth = maxDepth - depth

	if depth == maxDepth or entry.result != "*":
		entry.maxScore = evaluator.evaluator(board, entry.result)
		entry.minScore = entry.maxScore
		if transTable.size == transTable.maxSize and newEntry:
			transTable.table.popitem()
			transTable.size = transTable.size - 1
		entry.finalBoardPos = board.fen()
		transTable.table[entry.zobristHash] = entry
		transTable.size = transTable.size + 1
		return (None, entry.minScore)

	maxScore = -(1<<128)
	score = maxScore
	bestMove = None

	for move in board.legal_moves:
		board.push(move)
		score = -negamax(board, maxDepth, depth + 1, -gamma, transTable)[1]
		board.pop()

		if score > maxScore:
			maxScore = score
			bestMove = move

		if maxScore >= gamma:
			break

	if maxScore < gamma:
		entry.maxScore = maxScore
	else:
		entry.minScore = maxScore
	entry.bestMove = bestMove
	if (transTable.size == transTable.maxSize and newEntry):
		transTable.table.popitem()
		transTable.size = transTable.size - 1
	board.push(bestMove)
	entry.finalBoardPos = transTable.table[board.zobrist_hash()].finalBoardPos
	board.pop()
	transTable.table[entry.zobristHash] = entry
	transTable.size = transTable.size + 1
	return (bestMove, maxScore)


"""def mtd(board, maxDepth, guess, transTable, maxIter):
	gamma = 0
	move = None
	for i in xrange(maxIter):
		gamma = guess
		#(move, guess) = negamax(board, maxDepth, 0, gamma - 1, transTable)
		(move, guess) = ABnegamax(board, maxDepth, 0, gamma - 1, gamma, transTable)
		if gamma == guess:
			#print i,
			break
	return (move, guess)"""

def mtd(board, maxDepth, firstGuess, transTable, maxIter):
	guess = firstGuess
	upperBound = config.MAX_SCORE
	lowerBound = -(config.MAX_SCORE)
	while lowerBound < upperBound:
		#gamma = max(guess, lowerBound + 1)
		if guess == lowerBound:
			gamma = guess + 1
		else:
			gamma = guess
		(move, guess) = ABnegamax(board, maxDepth, 0, gamma - 1, gamma, transTable)
		if guess < gamma:
			upperBound = guess
		else:
			lowerBound = guess
	return (move, guess)

def mtdf(board, maxDepth, transTable, maxIter):
	guess1 = 1<<128
	guess2 = 1<<128

	for depth in xrange(2, maxDepth + 1):
		if depth % 2 == 0:
			(move, guess1) = mtd(board, depth, guess1, transTable, maxIter)
		else:
			(move, guess2) = mtd(board, depth, guess2, transTable, maxIter)

	if maxDepth % 2 == 0:
		return (move, guess1)
	else:
		return (move, guess2)