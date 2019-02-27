import sys
import random
import signal
import time
import copy


class Bot:

	def __init__(self):
		self.cell_weight = ((3,2,3),(2,4,2),(3,2,3)) # weight of winning position[i][j]
		self.board1heuristic = {} # store calculated board heuristics
		self.board2heuristic = {} # store calculated board heuristics
		self.blockheuristic_block1 = {} # store calculated block heuristics
		self.blockheuristic_block2 = {} # store calculated block heuristics
		self.boardHash = long(0)
		self.blockHash = [[long(0) for j in xrange(4)] for i in xrange(4)]
		self.blockPoints = 50
		patterns = [((0,0), (1,1), (2,2)), ((0,2),(1,1),(2,0)) ,((0, 0), (0, 1), (0, 2)), ((0, 0), (1, 0), (2, 0)), ((1, 0), (1, 1), (1, 2)), ((0, 1), (1, 1), (2, 1)), ((2, 0), (2, 1), (2, 2)), ((0, 2), (1, 2), (2, 2))]

		self.patterns = tuple(patterns)

	def oppFlag(self, flag):
		# NOT operation on flag
		return 'o' if flag == 'x' else 'x'

	def block_heuristic(self, flag, block):
		# Not just the places of flags, but also their relative position contributes to heuristic
		blockHeur = 0

		for pos_arr in self.patterns:
			blockHeur += self.pattern_checker(flag,block,pos_arr)

		# Finally, contribution of place (for settling tie-breakers, etc)
		for i in xrange(3):
			for j in xrange(3):
				if block[i][j] == flag:
					blockHeur += 0.1 * self.cell_weight[i][j]

		return blockHeur

	def board_heuristic(self, blockHeurs):
		boardHeur = 0
		for i in xrange(3):
			for j in xrange(3):
				if blockHeurs[i][j] > 0:
					boardHeur += 0.5 * blockHeurs[i][j]

		return boardHeur