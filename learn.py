import chess
import random
import chess.pgn
import negamax
#from ttable import ttableEntry
import ttable
import weights
import evaluator
import config

def main():

	#Open the pgn file with games to learn from
	games = open("GMallboth.pgn")
	#Initialize stuff
	counter = 0
	transTable = ttable.ttable()
	wInit = list(weights.initPosPnts)
	wFin = list(weights.finalPosPnts)
	learningRate = config.ALPHA_INIT

	while (True):
		#Read game
		game = chess.pgn.read_game(games)
		try:
			game.variation(0)
		except KeyError:
			continue
		if not game:
			break
		state = game

		#Go to end of game
		while not state.is_end():
			state = state.variation(0)

		#Find winner
		whitePnt = game.headers["Result"][0]
		if whitePnt == "1" and game.headers["Result"][1] != "/":
			winColor = True
		elif whitePnt == "0":
			winColor = False
		else:
			continue

		print "\nGame ", counter + 1

		#Clear transposition tables
		transTable.table.clear()
		transTable.size = 0

		for color in xrange(2):

			#Initialize stuff
			board = state.board()
			if winColor == color:
				scores = [config.MAX_SCORE]
			else:
				scores = [-config.MAX_SCORE]
			boards = []
			featuresInit = []
			featuresFinal = []
			boards.append(board.copy())
			turnCounter = 0
			if color:
				print "White"
			else:
				print "Black"

			#Backprop through game, storing scores and features. Might as well do this in forward prop, will revise later
			while not game.board() == board:
				board.pop()
				if board.turn == color:
					#transTable.table.clear()
					#transTable.size = 0
					#guess = negamax.ABnegamax(board, config.MAX_DEPTH, 0, -(config.MAX_SCORE), (config.MAX_SCORE), transTable)[1]
					#guess = negamax.mtd(board, config.MAX_DEPTH, config.MAX_SCORE, transTable, config.MAX_ITER_MTD)[1]
					scores.append(negamax.mtdf(board, config.MAX_DEPTH, transTable, config.MAX_ITER_MTD)[1])
					finalBoardPos = chess.Board(transTable.table[board.zobrist_hash()].finalBoardPos)
					boards.append(finalBoardPos)
					fI, fF = evaluator.findFeatures(finalBoardPos, color)
					featuresInit.append(fI)
					featuresFinal.append(fF)

					turnCounter = turnCounter + 1
					print "Turn ", turnCounter, '\r',
			print '\n',

			#Reverse lists, because I was too lazy to do stuff in forward prop
			scores.reverse()
			boards.reverse()
			featuresInit.reverse()
			featuresFinal.reverse()

			#Learn piece square tables
			wInit, wFin = learn(wInit, wFin, featuresInit, featuresFinal, scores, learningRate, config.LAMBDA, config.MAX_POSITION_SCORE)
			learningRate /= config.ALPHA_DEC_FACTOR
			#Write piece square tables to file
			f = open("weights.py", "w")
			f.write("initPosPnts = " + str(wInit) + "\nfinalPosPnts = " + str(wFin))
			f.close()
			#Update piece square tables in memory
			weights.initPosPnts = list(wInit)
			weights.finalPosPnts = list(wFin)

			#Debug info
			"""print scores
			#print featuresInit[10]
			#print featuresFinal[10]
			print transTable.hits
			print transTable.notHits
			print transTable.size
			#print wInit"""

		counter = counter + 1
		if counter == config.MAX_GAMES:
			break
	games.close()

def initializeWeights():
	initPosPnts = [[0 for i in range (0, 64)] for j in range (0, 6)]
	finalPosPnts = [[0 for i in range (0, 64)] for j in range (0, 6)]
	f = open("weights.py", "w")
	f.write("initPosPnts = " + str(initPosPnts) + "\nfinalPosPnts = " + str(finalPosPnts))
	f.close()
	weights.initPosPnts = initPosPnts
	weights.finalPosPnts = finalPosPnts

def learn(wRawInit, wRawFin, fInit, fFinal, J, alpha, lambdaDecay, clampVal):
	wInit = []
	wFin = []
	sizeJ = len(J)

	#unrolling parameters into vector
	for j in range(6):
		for i in range(64):
			wInit.append(wRawInit[j][i])
			wFin.append(wRawFin[j][i])
	sizeW = len(wInit)

	#calculate update amount (with sign) for parameters	
	updateMagInit = updateMagFinal = [0 for i in range(sizeW)]
	for t in range(sizeJ - 1):
		propTempDiff = 0 #propagated temporal difference
		for j in range(t, sizeJ - 1):
			propTempDiff += lambdaDecay**(j - t) * (J[j + 1] - J[j])
		updateMagInit = [updateMagInit[i] + (propTempDiff * fInit[t][i]) for i in range(sizeW)]
		updateMagFinal = [updateMagFinal[i] + (propTempDiff * fFinal[t][i]) for i in range(sizeW)]

	#update parameters
	for i in range(len(wInit)):
		wInit[i] += alpha * updateMagInit[i]
		wFin[i] += alpha * updateMagFinal[i]

	#rolling parameter vector
	wRawInit = [[max(min(int(round(wInit[i + 64*j])), clampVal), -clampVal) for i in range (0, 64)] for j in range (0, 6)]
	wRawFin = [[max(min(int(round(wFin[i + 64*j])), clampVal), -clampVal) for i in range (0, 64)] for j in range (0, 6)]

	#return final weights
	return (wRawInit, wRawFin)

initializeWeights()
main()