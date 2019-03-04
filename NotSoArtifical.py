import random
import time
from copy import deepcopy

class Bot:

    def __init__(self):
            self.begin = 0
            self.broke = False
            self.timeLimit = 22.7

            self.cell_weight = ((3,2,3),(2,4,2),(3,2,3)) #cell scores
            self.small_board1_weight = [[0,0,0],[0,0,0],[0,0,0]] #check small boards scores of board1
            self.small_board2_weight = [[0,0,0],[0,0,0],[0,0,0]] #check small boards scores of board2
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


    def update(self,board, old_move, new_move, ply):
        #updating the game board and small_board status as per the move that has been passed in the arguements
        board.big_boards_status[new_move[0]][new_move[1]][new_move[2]] = ply

        x = new_move[1]/3
        y = new_move[2]/3
        k = new_move[0]
        fl = 0

        #checking if a small_board has been won or drawn or not after the current move
        bs = board.big_boards_status[k]
        for i in range(3):
            #checking for horizontal pattern(i'th row)
            if (bs[3*x+i][3*y] == bs[3*x+i][3*y+1] == bs[3*x+i][3*y+2]) and (bs[3*x+i][3*y] == ply):
                board.small_boards_status[k][x][y] = ply
                return 'SUCCESSFUL', True
            #checking for vertical pattern(i'th column)
            if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == ply):
                board.small_boards_status[k][x][y] = ply
                return 'SUCCESSFUL', True
        #checking for diagonal patterns
        #diagonal 1
        if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return 'SUCCESSFUL', True
        #diagonal 2
        if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
            board.small_boards_status[k][x][y] = ply
            return 'SUCCESSFUL', True
        #checking if a small_board has any more cells left or has it been drawn
        for i in range(3):
            for j in range(3):
                if bs[3*x+i][3*y+j] =='-':
                    return 'SUCCESSFUL', False
        board.small_boards_status[k][x][y] = 'd'
        return 'SUCCESSFUL', False

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
                        big_board_Heur += 0.5 * self.small_board1_weight[i][j] #check
                elif flip ==2:
                    if self.small_board2_weight[i][j] > 0:
                        big_board_Heur += 0.5 * self.small_board2_weight[i][j]#check
        return big_board_Heur

    # The main heuristic function
    #passing the gameBoard(2BigBoards, 18Smallboards) of the game
    def heuristic(self, flag, gameBoard):
        #check the first two lines while implementing hash 

        total = 0

        #check below lines change according to naming convention in search
        sb1 = gameBoard.small_boards_status[0]
        sb2 = gameBoard.small_boards_status[1]
        bb1 = gameBoard.big_boards_status[0]
        bb2 = gameBoard.big_boards_status[1]

        #check should try optimizing "Two times looping" for board1 and board2
        for i in xrange(3):
            for j in xrange(3):
                if sb1[i][j] == flag:
                    self.small_board1_weight[i][j] = self.small_board_Points
                elif sb1[i][j] == self.oppFlag(flag) or sb1[i][j] == 'd':
                    self.small_board1_weight[i][j] = 0
                else:
                    block = tuple([tuple(bb1[3 * i + x][3 * j:3 * (j + 1)]) for x in xrange(3)])
                    self.small_board1_weight[i][j] = self.small_board_heuristic(flag, block)


        for i in xrange(3):
            for j in xrange(3):
                if sb2[i][j] == flag:
                    self.small_board2_weight[i][j] = self.small_board_Points
                elif sb2[i][j] == self.oppFlag(flag) or sb2[i][j] == 'd':
                    self.small_board2_weight[i][j] = 0
                else:
                    block = tuple([tuple(bb2[3 * i + x][3 * j:3 * (j + 1)]) for x in xrange(3)])
                    self.small_board2_weight[i][j] = self.small_board_heuristic(flag, block)

        #cal bigboard1 score
        big_board1_score = self.big_board_heuristic(flag, sb1, 1)

        #cal bigboard2 score
        big_board2_score = self.big_board_heuristic(flag, sb2, 2)


        total = big_board1_score + big_board2_score
        
        return total


    #only to check just did the same old implementation
    def hash_init(self):
        for l in xrange (2):
            for i in xrange(9):
                for j in xrange(9):
                    for k in xrange(2):
                        self.randTable[l][i][j][k] = long(random.randint(1, 2 ** 64))
                    

    def addMovetoHash(self, cell, player):
        x = cell[1]
        y = cell[2]
        
        if cell[0] == 0:
            self.big_board1Hash ^= self.randTable[0][x][y][player]
            self.small_board1Hash[x/3][y/3] ^= self.randTable[0][x][y][player]
        else:
            self.big_board2Hash ^= self.randTable[1][x][y][player]
            self.small_board2Hash[x/3][y/3] ^= self.randTable[1][x][y][player]

    def minimax(self, old_move, depth, max_depth, alpha, beta, isMax, board, my_flag, best_node, bonus_move):
        if time.time() - self.timeLimit > self.begin:
            self.broke = True
            return (-1.23456, (-1, -1))

        opp_flag = self.oppFlag(my_flag)

        terminal_state = board.find_terminal_state()
        if terminal_state[1] == 'WON':
            if terminal_state[0] == my_flag:
                return (1e5, old_move)
            elif terminal_state[0] == opp_flag:
                return (-1e5, old_move)

        if depth == max_depth:
            q1 = self.heuristic(self.who, board)
            q2 = self.heuristic(opp_flag, board)
            utility = q1 - (q2*(2))
            return (utility, old_move)

        else:
            children_list = board.find_valid_move_cells(old_move)
            random.shuffle(children_list)

            if len(children_list) == 0:
                q1 = self.heuristic(self.who, board)
                q2 = self.heuristic(opp_flag, board)
                utility = q1 - (q2*(2))
                return (utility, old_move)

            for child in children_list:
                if isMax:
                    self.update(board,old_move, child, my_flag)
                else:
                    self.update(board,old_move, child, opp_flag)

                my_flag_won = False
                opp_flag_won = False

                p_block = board.small_boards_status[child[0]]

                if p_block[child[1]/3][child[2]/3] == my_flag:
                    my_flag_won = True

                elif p_block[child[1]/3][child[2]/3] == opp_flag:
                    opp_flag_won = True

                if isMax and not my_flag_won:
                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, False, board, my_flag, best_node, 0)

                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        self.broke = True
                        return (-1.23456, (-1, -1))

                    if (score[0] > alpha):
                        best_node = child
                        alpha = score[0]

                elif isMax and my_flag_won and bonus_move < 2:

                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, True, board, my_flag, best_node, bonus_move+1)
                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        self.broke = True
                        return (-1.23456, (-1, -1))

                    if (score[0] > alpha):
                        alpha = score[0]
                        best_node = child

                elif isMax and my_flag_won and not bonus_move < 2:

                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, False, board, my_flag, best_node, 0)
                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        self.broke = True
                        return (-1.23456, (-1, -1))

                    if (score[0] > alpha):
                        alpha = score[0]
                        best_node = child
                elif not isMax and not opp_flag_won:

                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, True, board, my_flag, best_node, 0)

                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        return (-1.23456, (-1, -1))

                    if (score[0] < beta):
                        beta = score[0]
                        best_node = child
                elif not isMax and opp_flag_won and bonus_move < 2:

                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, False, board, my_flag, best_node, bonus_move+1)
                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        return (-1.23456, (-1, -1))

                    if (score[0] < beta):
                        beta = score[0]
                        best_node = child

                elif not isMax and opp_flag_won and not bonus_move < 2:

                    score = self.minimax(
                        child, depth+1, max_depth, alpha, beta, True, board, my_flag, best_node, 0)
                    if time.time() - self.timeLimit > self.begin:
                        board.big_boards_status[child[0]
                                                ][child[1]][child[2]] = '-'
                        board.small_boards_status[child[0]
                                                  ][child[1] / 3][child[2] / 3] = '-'
                        return (-1.23456, (-1, -1))

                    if (score[0] < beta):
                        beta = score[0]
                        best_node = child
                board.big_boards_status[child[0]][child[1]][child[2]] = '-'
                board.small_boards_status[child[0]
                                          ][child[1] / 3][child[2] / 3] = '-'

                if (alpha >= beta):
                    break
            if isMax:
                return (alpha, best_node)
            else:
                return (beta, best_node)
                

    def move(self, board, old_move, flag):
        self.begin = time.time()

        #check
        if old_move == (-1, -1, -1):
            self.addMovetoHash((1, 4, 4), 1)
            return (1, 4, 4)
        else:
            if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.oppFlag(flag):
                self.addMovetoHash(old_move, 0)

        self.who = flag

        maxDepth = 3

        validCells = board.find_valid_move_cells(old_move)
        random.shuffle(validCells)
        bestMove = validCells[0]

        while time.time() - self.begin < self.timeLimit:
            self.bigboard1HashSafeCopy = deepcopy(self.big_board1Hash)
            self.bigboard2HashSafeCopy = deepcopy(self.big_board2Hash)
            self.smallboard1HashSafeCopy = deepcopy(self.small_board1Hash)
            self.smallboard2HashSafeCopy = deepcopy(self.small_board2Hash)
            b = deepcopy(board)
            self.broke = False
            mini_max = self.minimax(old_move, 0, maxDepth, float("-inf"), float("inf"), True, b, self.who, (1, 1, 1), 0)
            move = mini_max[1]
            if not self.broke:
                bestMove = move
                maxDepth += 1
            else:
                self.big_board1Hash = self.bigboard1HashSafeCopy
                self.big_board2Hash = self.bigboard2HashSafeCopy
                self.small_board1Hash = self.smallboard1HashSafeCopy
                self.small_board2Hash = self.smallboard2HashSafeCopy
                break

            del b
        self.addMovetoHash(bestMove, 1)
        return bestMove
