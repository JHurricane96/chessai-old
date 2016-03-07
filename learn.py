import chess
import random
import chess.pgn
import negamax
#from ttable import ttableEntry
import ttable
import weights
import evaluator

MAX_ITER_MTD = 100
MAX_DEPTH = 3
ALPHA_INIT = 0.01
ALPHA_DEC_FACTOR = 1.003
LAMBDA = 0.7

def main():

	#Open the pgn file with games to learn from
	games = open("GMallboth.pgn")
	#Initialize stuff
	counter = 0
	transTable = ttable.ttable()
	wInit = weights.initPosPnts
	wFin = weights.finalPosPnts
	learningRate = ALPHA_INIT

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
		board = state.board()
		whitePnt = game.headers["Result"][0]
		if whitePnt == "1" and game.headers["Result"][1] != "/":
			color = True
		elif whitePnt == "0":
			color = False
		else:
			continue

		print "\nGame ", counter + 1

		#Initialize stuff
		scores = [evaluator.MAX_SCORE]
		boards = []
		featuresInit = []
		featuresFinal = []
		boards.append(board.copy())
		transTable.table.clear()
		transTable.size = 0
		turnCounter = 0

		#Backprop through game, storing scores and features. Might as well do this in forward prop, will revise later
		while not game.board() == board:
			board.pop()
			if board.turn == color:
				#transTable.table.clear()
				#transTable.size = 0
				#guess = negamax.ABnegamax(board, MAX_DEPTH, 0, -(evaluator.MAX_SCORE), (evaluator.MAX_SCORE), transTable)[1]
				#guess = negamax.mtd(board, MAX_DEPTH, evaluator.MAX_SCORE, transTable, MAX_ITER_MTD)[1]
				scores.append(negamax.mtdf(board, MAX_DEPTH, transTable, MAX_ITER_MTD)[1])
				boards.append(chess.Board(transTable.table[board.zobrist_hash()].finalBoardPos))
				fI, fF = evaluator.findFeatures(board, color)
				featuresInit.append(fI)
				featuresFinal.append(fF)

				turnCounter = turnCounter + 1
				print "Turn ", turnCounter, '\r'
		print '\n'

		#Reverse lists, because I was too lazy to do stuff in forward prop
		scores.reverse()
		boards.reverse()
		featuresInit.reverse()
		featuresFinal.reverse()

		#Learn piece square tables
		wInit, wFin = learn(wInit, wFin, featuresInit, featuresFinal, scores, learningRate, LAMBDA)
		learningRate /= ALPHA_DEC_FACTOR
		#Write piece square tables to file
		f = open("weights.py", "w")
		f.write("initPosPnts = " + str(wInit) + "\nfinalPosPnts = " + str(wFin))
		f.close()

		#Debug info
		"""print scores
		#print featuresInit[10]
		#print featuresFinal[10]
		print transTable.hits
		print transTable.notHits
		print transTable.size
		#print wInit"""
		counter = counter + 1
		if counter == 50:
			break
	games.close()

def initializeWeights():
	initPosPnts = [[[1 for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]
	finalPosPnts = [[[1 for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]
	f = open("weights.py", "w")
	f.write("initPosPnts = " + str(initPosPnts) + "\nfinalPosPnts = " + str(finalPosPnts))
	f.close()

def learn(wRawInit, wRawFin, fInit, fFinal, J, alpha, lambdaDecay):
	wInit = []
	wFin = []
	sizeJ = len(J)

	#unrolling parameters into vector
	for k in range(2):
		for j in range(6):
			for i in range(64):
				wInit.append(wRawInit[k][j][i])
				wFin.append(wRawFin[k][j][i])
	sizeW = len(wInit)

	#calculate update amount (with sign) for parameters	
	updateMagInit = updateMagFinal = [0 for i in range(sizeW)]
	for t in range(sizeJ - 1):
		propTempDiff = 0 #propogated temporal difference
		for j in range(t, sizeJ - 1):
			propTempDiff += lambdaDecay**(j - t) * (J[j + 1] - J[j])
		updateMagInit = [updateMagInit[i] + (propTempDiff * fInit[t][i]) for i in range(sizeW)]
		updateMagFinal = [updateMagFinal[i] + (propTempDiff * fFinal[t][i]) for i in range(sizeW)]

	#update parameters
	for i in range(len(wInit)):
		wInit[i] += alpha * updateMagInit[i]
		wFin[i] += alpha * updateMagFinal[i]

	#rolling parameter vector
	wRawInit = [[[int(round(wInit[i + 64*j + 64*6*k])) for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]
	wRawFin = [[[int(round(wFin[i + 64*j + 64*6*k])) for i in range (0, 64)] for j in range (0, 6)] for k in range (0, 2)]

	#return final weights
	return (wRawInit, wRawFin)


main()