from random import randint
from BaseAI import BaseAI
from Displayer import Displayer
import sys
from Grid import Grid
import time
import math
from copy import deepcopy

MAX_INT = sys.maxint
MIN_INT = (-1)*MAX_INT

sys.setrecursionlimit(10000)

actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

directionVec = [(-1, 0), (1, 0), (0, -1), (0, 1)]

displayer = Displayer()

possibleTiles = [2, 4]
defaultProbability = 0.9

class PlayerAI(BaseAI):

    def getMove(self, grid):
        # cells = grid.getAvailableCells()

        start_time = time.clock()

        # do iterative deepening
        depth_limit = 1

        gridCopy = Grid()
        gridCopy.map = deepcopy(grid.map)
        child, util, move = self.maximize(gridCopy, MIN_INT, MAX_INT, start_time, 0, depth_limit)
        maxUtil, maxMove = util, move

        while time.clock() - start_time < 0.08:
            depth_limit += 1
            gridCopy = Grid()
            gridCopy.map = deepcopy(grid.map)
            child, util, move = self.maximize(gridCopy, MIN_INT, MAX_INT, start_time, 0, depth_limit)
            if util > maxUtil:
                maxUtil, maxMove = util, move

        # print "\n"
        # displayer.display(child)
        # print maxUtil, depth_limit
        # print time.clock() - start_time
        return maxMove

    def minimize(self, grid, alpha, beta, start_time, depth, depth_limit):
        if self.terminal_test(grid, start_time, depth, depth_limit):
            return grid, self.eval_heuristic(grid)
        
        newGrid = Grid()

        minChild, minUtility = newGrid, MAX_INT

        availableCells = grid.getAvailableCells()

        for (x, y) in availableCells:
            gridCopy = Grid()
            gridCopy.map = deepcopy(grid.map)

            if randint(0,99) < 100 * defaultProbability:
                gridCopy.insertTile((x,y), possibleTiles[0])
            else:
                gridCopy.insertTile((x,y), possibleTiles[1])
            
            child, utility, m = self.maximize(gridCopy, alpha, beta, start_time, depth+1, depth_limit)

            if utility < minUtility:
                minChild, minUtility = gridCopy, utility

            if minUtility <= alpha:
                break

            if minUtility < beta:
                beta = minUtility

        return (minChild, minUtility)
    
    def maximize(self, grid, alpha, beta, start_time, depth, depth_limit):
        if self.terminal_test(grid, start_time, depth, depth_limit):
            return (grid, self.eval_heuristic(grid), None)

        newGrid = Grid()

        maxChild, maxUtility, move = newGrid, MIN_INT, None

        availableMoves = grid.getAvailableMoves()

        for i in availableMoves:
            gridCopy = Grid()
            gridCopy.map = deepcopy(grid.map)
            gridCopy.move(i)

            child, utility = self.minimize(gridCopy, alpha, beta, start_time, depth+1, depth_limit)

            if utility > maxUtility:
                maxChild, maxUtility, move = gridCopy, utility, i

            if maxUtility >= beta:
                break

            if maxUtility > alpha:
                alpha = maxUtility

        return (maxChild, maxUtility, move)

    def terminal_test(self, grid, start_time, depth, depth_limit):
        if time.clock() - start_time >= 0.08:
            return True
        if depth > depth_limit:
            return True
        if grid.canMove():
            # if grid.getMaxTile() == 2048:
            #     return True
            # else:
            #     return False
            return False
        else:
            return True

    def eval_heuristic(self, grid):#, start_time, depth):
        # assign weights to the different heuristics
        smoothWeight = 0.1
        monoWeight = 1.0
        emptyWeight = 2.7
        maxWeight = 1.0

        num_empty_cell = self.empty_cell_h(grid)
        # avg_non_empty_cell_value = self.average_non_empty_cell_value_h(grid)
        max_cell_value = self.max_cell_value_h(grid)
        monotonicity_score = self.monotonicity_h(grid)
        smoothness_score = self.smoothness_h(grid)
        # corner_max_value = self.corner_max_value_h(grid)
        return monoWeight*monotonicity_score +  smoothWeight*smoothness_score + emptyWeight*(num_empty_cell) + maxWeight*max_cell_value

    def empty_cell_h(self, grid):
        # the more available cells there is, the more promising the state
        return len(grid.getAvailableCells())

    def max_cell_value_h(self, grid):
        # get more of large values, instead of looking at the maximum value ONLY
        return grid.getMaxTile()

    def average_non_empty_cell_value_h(self, grid):
        # the larger the average non-empty cell value, the more promising the state
        num_non_empty_cell = 0
        sum_non_empty_cell = 0
        for i in range(4):
            for j in range(4):
                if grid.getCellValue((i,j)) != 0:
                    sum_non_empty_cell += grid.getCellValue((i,j))
                    num_non_empty_cell += 1
        return 1.0*sum_non_empty_cell/num_non_empty_cell

    # trying
    # def monotonic_alignment_h(self, grid):
    #   # monotonic_score = 0
    #   # alignment_score = 0
    #   row_score = 0
    #   col_score = 0
    #   for n in range(4):
    #       # horizontally, check if all cells in a column are monotonically increasing - monotonic score++, or decreasing - monotonic score--, or equal - alignment score++; skip 0 cell? - will this deincentivise the max value staying on the edge
    #       row_monotonic_score = 0
    #       row_alignment_score = []
    #       # row_alignment_score stores all the equal cells side by side
    #       max_row_value = 0
    #       sum_row_value = 0
    #       for i in range(4-1):
    #           # update maximum value in row to multiply for row score
    #           if grid.getCellValue((i, n)) > max_row_value:
    #               max_row_value = grid.getCellValue((i, n))
    #           # if grid.getCellValue((i, n)) == 0:
    #           #   continue

    #           if grid.getCellValue((i, n)) < grid.getCellValue((i+1, n)):
    #               row_monotonic_score += grid.getCellValue((i+1, n)) - grid.getCellValue((i, n))
    #           elif grid.getCellValue((i, n)) > grid.getCellValue((i+1,n)):
    #               row_monotonic_score -= grid.getCellValue((i+1, n)) - grid.getCellValue((i, n))
    #           else:
    #               row_alignment_score.append(grid.getCellValue((i,n)))
    #       # if abs(row_monotonic_score) + len(row_alignment_score) >= 2:
    #       #   row_score += max_row_value * 3 + sum(row_alignment_score)
    #       # else:
    #       #   row_score += abs(row_monotonic_score) + sum(row_alignment_score)# + max_row_value
    #       row_score += abs(row_monotonic_score) + sum(row_alignment_score)
    #       # the heuristic prioritises monotonically increasing or decreasing cell sequence + possible merged cell values

    #       col_monotonic_score = 0
    #       col_alignment_score = []
    #       # row_alignment_score stores all the equal cells stacked together
    #       max_col_value = 0
    #       # perpendicularly, check if all cells in a row are monotonically increasing - monotonic score++, or decreasing - monotonic score--, or equal - alignment score++; skip 0 cell?
    #       for j in range(4-1):
    #           # update maximum value in row to multiply for col score
    #           if grid.getCellValue((n, j)) > max_col_value:
    #               max_col_value = grid.getCellValue((i, n))
    #           # if grid.getCellValue((n, j)) == 0:
    #           #   continue

    #           if grid.getCellValue((n, j)) < grid.getCellValue((n, j+1)):
    #               col_monotonic_score += grid.getCellValue((n, j+1)) - grid.getCellValue((n, j))
    #           elif grid.getCellValue((n, j)) > grid.getCellValue((n, j+1)):
    #               col_monotonic_score -= grid.getCellValue((n, j+1)) - grid.getCellValue((n, j))
    #           else:
    #               col_alignment_score.append(grid.getCellValue((n,j)))

    #       # if abs(col_monotonic_score) + len(col_alignment_score) >= 2:
    #       #   col_score += max_col_value * 3 + sum(col_alignment_score)
    #       # else:
    #       #   col_score += abs(col_monotonic_score) + sum(col_alignment_score)# + max_col_value
    #       col_score += abs(col_monotonic_score) + sum(col_alignment_score)
    #       # the heuristic prioritises monotonically increasing or decreasing cell sequence + possible merged cell values

    #   return row_score + col_score


    def corner_max_value_h(self, grid):
        # if any of the max tile(s) is at the corner of the grid, return 1; else return 0
        maxValue = grid.getMaxTile()
        maxTile = []
        for i in range(4):
            for j in range(4):
                if grid.getCellValue((i,j)) == maxValue:
                    maxTile.append((i,j))
                    if (i == 3 and j == 3):# or (i == 0 and j == 3) or (i == 0 and j == 0) or (i == 3 and j == 0):
                        return 1
        return 0

    def smoothness_h(self, grid):
        # measures in two directions (down, right), how smooth are the cells in log(2) scale. This is represented as a penalty score
        smoothness = 0
        for i in range(4):
            for j in range(4):
                if grid.getCellValue((i,j))>0:
                    value = math.log(grid.getCellValue((i,j)),2)
                    for index in range(1,3):
                        direction = directionVec[index]
                        move = 1
                        nextVal = grid.getCellValue((i+move*direction[0],j+move*direction[1]))
                        # find the farthest cell that is not empty and not out of bound
                        while (nextVal == 0 and (not grid.crossBound((i+move*direction[0],j+move*direction[1])))):
                            move += 1
                            nextVal = grid.getCellValue((i+move*direction[0],j+move*direction[1]))
                        # don't update unless non-empty neighbour cell is found
                        if nextVal > 0:
                            smoothness -= abs(value - math.log(nextVal,2))
        return smoothness

    def monotonicity_h(self, grid):
        # measures how monotonic the grid is in up/down and left/right directions
        total = [0, 0, 0, 0]

        # up/down directions
        for i in range(4):
            cur = 0
            nex = cur+1
            while (nex < 4):
                while (nex < 4 and grid.getCellValue((i,nex)) == 0):
                    nex += 1
                if nex > 4:
                    nex -= 1
                if grid.getCellValue((i,cur)) > 0:
                    curValue = math.log(grid.getCellValue((i,cur)),2)
                else:
                    curValue = 0
                if grid.getCellValue((i,nex)) > 0:
                    nextValue = math.log(grid.getCellValue((i,nex)),2)
                else:
                    nextValue = 0

                # decrement the score in the up direction, if top is greater than below
                if curValue > nextValue:
                    total[0] += nextValue - curValue
                # decrement the score in the down direction, if below is greater than top
                elif nextValue > curValue:
                    total[1] += curValue - nextValue
                # move downward onto the next non empty cell
                cur = nex
                nex += 1


        # left/right directions
        for j in range(4):
            cur = 0
            nex = cur+1
            while (nex < 4):
                while (nex < 4 and grid.getCellValue((nex, j)) == 0):
                    nex += 1
                if nex > 4:
                    nex -= 1
                if grid.getCellValue((cur,j)) > 0:
                    curValue = math.log(grid.getCellValue((cur,j)),2) 
                else:
                    curValue = 0
                if grid.getCellValue((nex,j)) > 0:
                    nextValue = math.log(grid.getCellValue((nex,j)),2)
                else:
                    nextValue = 0

                # decrement the score in the left direction, if left is greater than right
                if curValue > nextValue:
                    total[2] += nextValue - curValue
                # decrement the score in the right direction, if right is greater than left
                elif nextValue > curValue:
                    total[3] += curValue - nextValue
                # move rightward onto the next non empty cell
                cur = nex
                nex += 1

        # in the up/down, left/right direction, get the least negative score along the axis, and sum them up
        return max(total[0], total[1]) + max(total[2], total[3])










