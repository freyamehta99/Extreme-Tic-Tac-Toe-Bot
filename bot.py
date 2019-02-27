import sys
import random
import signal
import time
import copy

class Bot:

    def __init__(self):
            self.cell_weight = ((3,2,3),(2,4,2),(3,4,3)) #cell scores
            self.block1_weight = ((0,0,0),(0,0,0),(0,0,0)) #check block scores of board1
            self.block2_weight = ((0,0,0),(0,0,0),(0,0,0)) #check block scores of board2
            self.board1hueristic = {} #stored scores of board1
            self.board2hueristic = {} #stored score of board2
            self.block1hueristic = {} #stored score of smallboard's in board1
            self.block2hueristic = {} #stored score of smallboard's in board2 #check later if this is required
            self.finalheuristic = {} #stored score of total state's #check
            self.finalHash = long(0)
            self.board1Hash = [long(0) for i in range (2)]
            self.board2Hash = [long(0) for i in range(2)]
            self.block1Hash = [[long(0) for j in xrange(3)] for i in xrange(3)]
            self.block2Hash = [[long(0) for j in xrange(3)] for i in xrange(3)]
            self.blockPoints = 50  # check why now
            patterns = [((0, 0), (1, 1), (2, 2)), ((0, 2), (1, 1), (2, 0)), ((0, 0), (0, 1), (0, 2)), ((0, 0), (1, 0), (2, 0)), ((
                        1, 0), (1, 1), (1, 2)), ((0, 1), (1, 1), (2, 1)), ((2, 0), (2, 1), (2, 2)), ((0, 2), (1, 2), (2, 2))]

            self.patterns = tuple(patterns) #fixed

    def oppFlag(self, flag):
        #get opposite flag
        return 'o' if flag == 'x' else 'x'

    #get the probability of every pattern in a block's and board's
    def pattern_checker(self, flag, block, pos_array):
        flagCount = 0
        for pos in pos_array:
            if block[pos[0]][pos[1]] == flag:
                flagCount += 1
            elif block[pos[0]][pos[1]] == self.oppFlag(flag):
                return 0
        if flagCount == 1:
            #1/3 pattern full. 1 point is given
            return 1
        elif flagCount == 2:
            #2/3 pattern full. 10 points are given
            return 10
        elif flagCount == 3:  #check if required
            #pattern finished. 50 points are given
            return 50
        return 0

    #cal score of individual block's
    def block_heuristic(self, flag, block):
        #consider position of the flag, And also the relative positions
        blockHeur = 0

        for pos_arr in self.patterns:
            blockHeur += self.pattern_checker(flag, block, pos_arr)

        for i in xrange(3):
            for j in xrange(3):
                if block[i][j] == flag:
                    blockHeur += 0.1 * self.cell_weight[i][j]
        return blockHeur


    #cal score of individual board's
    def board_heuristic(self, flag, blockHeurs, flip):
        #consider the weights of blocks
        # the relative posiiton of blocks won are considered in **board_**pattern_checker
        boardHeur = 0

        for pos_arr in self.patterns:#check
            boardHeur += self.pattern_checker(flag, blockHeurs, pos_arr)

        for i in xrange(3):
            for j in xrange(3):
                if flip == 1:
                    if self.block1_weight[i][j] > 0:
                        boardHeur += 0.5 * self.block1_weight[i][j]#check
                else:
                    if self.block2_weight[i][j] > 0:
                        boardHeur += 0.5 * self.block2_weight[i][j]#check
        return boardHeur


    # def board_pattern_checker(self, flag, pos_arr, blockHeurs):
    #     flagCount = 0
    #     for pos in pos_arr:
    #         if blockHeurs[pos[0]][pos[1]] == flag:
    #             flagCount += 1
    #         elif blockHeurs[pos[0]][pos[1]] == self.oppFlag(flag):
    #             return 0
    #     if flagCount == 1:
    #         #1/3 pattern full. 1 point is given
    #         return 1
    #     elif flagCount == 2:
    #         #2/3 pattern full. 10 points are given
    #         return 10
    #     elif flagCount == 3:  # check if required
    #         #pattern finished. 50 points are given
    #         return 50
    #     return 0 #check if required


    # The main heuristic function
    #passing the state(2BigBoards, 18Smallboards) of the game
    def heuristic(self, flag, state):
        #check the first two lines while implementing hash 
        if (self.finalHash, flag) in self.finalheuristic:
			return self.finalheuristic[(self.finalHash, flag)]#check for avoiding repeated calculations

        total = 0

        #check below lines change according to naming convention in search
        blocks1 = state.block1_status
        blocks2 = state.block2_status
        b1 = state.board1_status
        b2 = state.board2_status
        # blockHeurs1 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] #check hope not required
        
        #check should try optimizing "Two times looping" for board1 and board2
        for i in xrange(3):
            for j in xrange(3):
                if blocks1[i][j] == flag:
                    self.block1_weight = self.blockPoints
                elif blocks1[i][j] == self.oppFlag(flag) or blocks1[i][j] == 'd':
                    self.block1_weight[i][j] = 0
                else:
					block = tuple([tuple(b1[3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
					if (self.block1Hash[i][j], flag) in self.block1hueristic:
						self.block1_weight[i][j] = self.block1hueristic[(self.block1Hash[i][j], flag)]
					else:
						self.block1_weight[i][j] = self.block_heuristic(flag, block)
						self.block1hueristic[(self.block1Hash[i][j], flag)] = self.block1_weight[i][j]

        for i in xrange(3):
            for j in xrange(3):
                if blocks2[i][j] == flag:
                    self.block2_weight = self.blockPoints
                elif blocks2[i][j] == self.oppFlag(flag) or blocks2[i][j] == 'd':
                    self.block2_weight[i][j] = 0
                else:
					block = tuple([tuple(b2[3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
					if (self.block2Hash[i][j], flag) in self.block2hueristic:
						self.block2_weight[i][j] = self.block2hueristic[(
						    self.block2Hash[i][j], flag)]
					else:
						self.block2_weight[i][j] = self.block_heuristic(flag, block)
						self.block2hueristic[(self.block2Hash[i][j], flag)
                           ] = self.block2_weight[i][j]

        board1score = self.board_heuristic(flag, blocks1, 1)
        board2score = self.board_heuristic(flag, blocks2, 2)

        total = board1score + board2score
        
        self.finalheuristic[(self.finalHash, flag)] = total
        return total
