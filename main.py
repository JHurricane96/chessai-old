import chess
import ttable
import negamax

MAX_ITER_MTD = 100
MAX_DEPTH = 5

def main():
	board = chess.Board()
	guess = 1<<32
	transTable = ttable.ttable()
	while (True):
		rawMove = ""

		if board.is_game_over():
			break

		#move = negamax.ABnegamax(board, MAX_DEPTH, 0, -(1<<32), (1<<32), transTable)[0]
		#transTable.table.clear()
		#transTable.size = 0
		#move = negamax.mtd(board, MAX_DEPTH, 1<<32, transTable, MAX_ITER_MTD)[0]
		move = negamax.mtdf(board, MAX_DEPTH, transTable, MAX_ITER_MTD)[0]
		print move.uci()
		board.push(move)
		b = board.copy()
		f = open("swag.txt", "w")
		f.write(str(move) + "\n")
		f.write(str(b) + "\n")
		for i in xrange(MAX_DEPTH - 1):
			mv = transTable.table[b.zobrist_hash()].move
			f.write(mv.uci() + "\n")
			b.push(mv)
			f.write(str(b) + "\n")
		f.close()

		print board
		print board.fen()

		if board.is_game_over():
			break

		rawMove = ""
		while rawMove == "":
			rawMove = raw_input("Enter your move: ")
			try:
				move = chess.Move.from_uci(rawMove)
			except ValueError:
				rawMove = ""
				continue
			if (not move in board.legal_moves):
				rawMove = ""
		board.push(move)
		print board
		print board.fen()

main()