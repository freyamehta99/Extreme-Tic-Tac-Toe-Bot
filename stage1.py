import sys
import random
import signal
import time
from copy import deepcopy

class Bot:

    def __init__(self):
            self.cell_weight = ((3,2,3),(2,4,2),(3,4,3)) #cell scores
            self.small_board1_weight = ((0,0,0),(0,0,0),(0,0,0)) #check small boards scores of board1
            self.small_board2_weight = ((0,0,0),(0,0,0),(0,0,0)) #check small boards scores of board2
            self.big_board1hueristic = {} #stored scores of board1
            self.big_board2hueristic = {} #stored score of board2
            self.small_board1hueristic = {} #stored score of smallboard's in board1
            self.small_board2hueristic = {} #stored score of smallboard's in board2 #check later if this is required
            self.finalheuristic = {} #stored score of total state's #check
            self.finalHash = long(0)
            self.big_board1Hash = long(0)
            self.big_board2Hash = long(0)
            self.small_board1Hash = [[long(0) for j in xrange(3)] for i in xrange(3)]
            self.small_board2Hash = [[long(0) for j in xrange(3)] for i in xrange(3)]
            self.small_board_Points = 50  # check why now
            self.randTable = [[[[long(0) for l in xrange(2)] for j in xrange(9)] for i in xrange(
                9)] for k in xrange(2)]  # random strings for hash components
            patterns = [((0, 0), (1, 1), (2, 2)), ((0, 2), (1, 1), (2, 0)), ((0, 0), (0, 1), (0, 2)), ((0, 0), (1, 0), (2, 0)), ((
                        1, 0), (1, 1), (1, 2)), ((0, 1), (1, 1), (2, 1)), ((2, 0), (2, 1), (2, 2)), ((0, 2), (1, 2), (2, 2))]

            self.patterns = tuple(patterns) #fixed

    def oppFlag(self, flag):
        #get opposite flag
        return 'o' if flag == 'x' else 'x'

    #get the probability of every pattern in a small and big board's
    def pattern_checker(self, flag, board, pos_array):
        flagCount = 0
        for pos in pos_array:
            if board[pos[0]][pos[1]] == flag:
                flagCount += 1
            elif board[pos[0]][pos[1]] == self.oppFlag(flag):
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

    #cal score of individual small_boards's
    def small_board_heuristic(self, flag, small_board):
        #consider position of the flag, And also the relative positions
        small_board_Heur = 0

        for pos_arr in self.patterns:
            small_board_Heur += self.pattern_checker(flag, small_board, pos_arr)

        for i in xrange(3):
            for j in xrange(3):
                if small_board[i][j] == flag:
                    small_board_Heur += 0.1 * self.cell_weight[i][j]
        return small_board_Heur


    #cal score of individual board's
    def big_board_heuristic(self, flag, small_board_State, flip):
        #consider the weights of small_boards
        # the relative posiiton of small_boards won are considered in **board_**pattern_checker
        big_board_Heur = 0

        for pos_arr in self.patterns:#check
            big_board_Heur += self.pattern_checker(flag, small_board_State, pos_arr)

        for i in xrange(3):
            for j in xrange(3):
                if flip == 1:
                    if self.small_board1_weight[i][j] > 0:
                        big_board_Heur += 0.5 * self.small_board1_weight[i][j]#check
                else:
                    if self.small_board2_weight[i][j] > 0:
                        big_board_Heur += 0.5 * self.small_board2_weight[i][j]#check
        return big_board_Heur


    # def board_pattern_checker(self, flag, pos_arr, small_board_State):
    #     flagCount = 0
    #     for pos in pos_arr:
    #         if small_board_State[pos[0]][pos[1]] == flag:
    #             flagCount += 1
    #         elif small_board_State[pos[0]][pos[1]] == self.oppFlag(flag):
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
    #passing the gameBoard(2BigBoards, 18Smallboards) of the game
    def heuristic(self, flag, gameBoard):
        #check the first two lines while implementing hash 
        if (self.finalHash, flag) in self.finalheuristic:
			return self.finalheuristic[(self.finalHash, flag)]#check for avoiding repeated calculations

        total = 0

        #check below lines change according to naming convention in search
        sb1 = gameBoard.small_boards_status[0]
        sb2 = gameBoard.small_boards_status[1]
        bb1 = gameBoard.big_boards_status[0]
        bb2 = gameBoard.big_boards_status[1]
        # small_board_State1 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] #check hope not required
        
        #check should try optimizing "Two times looping" for board1 and board2
        for i in xrange(3):
            for j in xrange(3):
                if sb1[i][j] == flag:
                    self.small_board1_weight[i][j] = self.small_board_Points
                elif sb1[i][j] == self.oppFlag(flag) or sb1[i][j] == 'd':
                    self.small_board1_weight[i][j] = 0
                else:
					block = tuple([tuple(bb1[3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
					if (self.small_board1Hash[i][j], flag) in self.small_board1hueristic:
						self.small_board1_weight[i][j] = self.small_board1hueristic[(self.small_board1Hash[i][j], flag)]
					else:
						self.small_board1_weight[i][j] = self.small_board_heuristic(flag, block)
						self.small_board1hueristic[(self.small_board1Hash[i][j], flag)] = self.small_board1_weight[i][j]

        for i in xrange(3):
            for j in xrange(3):
                if sb2[i][j] == flag:
                    self.small_board2_weight[i][j] = self.small_board_Points
                elif sb2[i][j] == self.oppFlag(flag) or sb2[i][j] == 'd':
                    self.small_board2_weight[i][j] = 0
                else:
					block = tuple([tuple(bb2[3*i + x][3*j:3*(j+1)]) for x in xrange(3)])
					if (self.small_board2Hash[i][j], flag) in self.small_board2hueristic:
						self.small_board2_weight[i][j] = self.small_board2hueristic[(
						    self.small_board2Hash[i][j], flag)]
					else:
						self.small_board2_weight[i][j] = self.small_board_heuristic(flag, block)
						self.small_board2hueristic[(self.small_board2Hash[i][j], flag)
                           ] = self.small_board2_weight[i][j]

        #cal bigboard1 score
        if (self.big_board1Hash, flag) in self.big_board1hueristic:
            big_board1_score = self.big_board1hueristic[(self.big_board1Hash, flag)]
        big_board1_score = self.big_board_heuristic(flag, sb1, 1)
        self.big_board1hueristic[(self.big_board1Hash,flag)] = big_board1_score

        #cal bigboard2 score
        if (self.big_board2Hash, flag) in self.big_board2hueristic:
            big_board2_score = self.big_board2hueristic[(self.big_board2Hash, flag)]
        big_board2_score = self.big_board_heuristic(flag, sb2, 2)
        self.big_board2hueristic[(self.big_board2Hash, flag)] = big_board2_score


        total = big_board1_score + big_board2_score
        
        self.finalheuristic[(self.finalHash, flag)] = total
        return total


    #only to check just did the same old implementation
    def hash_init(self):
        # Every (position,player) pair is given a random bit-string
        for l in xrange (2):
            for i in xrange(9):
                for j in xrange(9):
                    for k in xrange(2):
                        self.randTable[l][i][j][k] = long(random.randint(1, 2 ** 64))
                    

    def addMovetoHash(self, cell, player):
        # player -> 0: opponent, 1: us
        x = cell[1]
        y = cell[2]
        
        if cell[0] == 0:
            self.big_board1Hash ^= self.randTable[0][x][y][player]
            self.small_board1Hash[x/3][y/3] ^= self.randTable[0][x][y][player]
        else:
            self.big_board2Hash ^= self.randTable[1][x][y][player]
            self.small_board2Hash[x/3][y/3] ^= self.randTable[1][x][y][player]


    def minimax(self, board, flag, depth, maxDepth, alpha, beta, old_move):
        checkGoal = board.find_terminal_state()

        if checkGoal[1] == 'WON':
            if checkGoal[0] == self.who:
                return float("inf"), "placeholder"
            else:
                return float("inf"), "placeholder"
        elif checkGoal[1] == "DRAW":
            return - 100000, "placeholder"
            
        if depth == maxDepth:
            return (self.heuristic(self.who, board) - self.heuristic(self.oppFlag(self.who), board)), "placeholder"
            
        validCells = board.find_valid_move_cells(old_move)
        validCells = random.shuffle(validCells)

        isMax = (flag == self.who)
        
        if isMax:
            maxVal = float("-inf")
            maxInd = 0
            for i in xrange(len(validCells)):
                cell = validCells[i]
                board.update(old_move, cell, flag)
                self.addMovetoHash(cell, 1)
                
                val = self.minimax(board, self.oppFlag(flag), depth + 1, maxDepth, alpha, beta, cell)[0]
                
                if val > maxVal:
                    maxVal = val
                    maxInd = i
                if maxVal > alpha:
                    alpha = maxVal

                board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
                board.small_boards_status[cell[0]][cell[1] / 3][cell[2] / 3] = '-'

                self.addMovetoHash(cell, 1)
                if beta <= alpha:
                    break
            return maxVal, validCells[maxInd]
            
        else:
            minVal = float("inf")
            minInd = 0
            for i in xrange(len(validCells)):
                cell = validCells[i]
                board.update(old_move, cell, flag)
                self.addMovetoHash(cell, 0)
                
                val = self.minimax(board, self.oppFlag(flag), depth + 1, maxDepth, alpha, beta, cell)[0]
                
                if val < minVal:
                    minVal = val
                if minVal < beta:
                    beta = minVal
                
                board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
                board.small_boards_status[cell[0]][cell[1 / 3]][cell[2 / 3]] = '-'
                
                self.addMovetoHash(cell, 0)
                
                if beta <= alpha:
                    break
        return minVal,"placeholder"


    def sig_handler(self, signum, frame):
        raise Exception("timeout")

    def move(self, board, old_move, flag):
        signal.signal(signal.SIGALRM, self.sig_handler)
        signal.alarm(20)

        #check
        if old_move == (-1, -1, -1):
            signal.alarm(0)
            self.addMovetoHash((1, 4, 4), 1)
            return (1, 4, 4)
            
        else:
            if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.oppFlag(flag):
                self.addMovetoHash(old_move, 0)
                
        self.who = flag

        maxDepth = 3

        validCells = board.find_valid_move_cells(old_move)
        bestMove = validCells[0]

        try:
            while True:
                self.bigboard1HashSafeCopy = self.big_board1Hash
                self.bigboard2HashSafeCopy = self.big_board2Hash
                self.smallboard1HashSafeCopy = deepcopy(self.small_board1Hash)
                self.smallboard2HashSafeCopy = deepcopy(self.small_board2Hash)
                b = deepcopy(board)
                move = self.minimax(b, flag, 0, maxDepth, float("-inf"), float("inf"), old_move)[1]
                bestMove = move
                maxDepth += 1
                del b

        except Exception as e:
            self.big_board1Hash = self.bigboard1HashSafeCopy
            self.big_board2Hash = self.bigboard2HashSafeCopy
            self.small_board1Hash = self.smallboard1HashSafeCopy
            self.small_board2Hash = self.smallboard2HashSafeCopy
            pass

        signal.alarm(0)

        self.addMovetoHash(bestMove, 1)
        
        return bestMove


