import copy
import random 
from eternity_puzzle import EternityPuzzle

GRAY = 0
BLACK = 23
RED = 24
WHITE = 25

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

def solve_heuristic(eternity_puzzle, r=random.random()):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    #################
    # CONFIGURATION #
    ##################################
    r = 0.18062110343039572
    random.seed(r)
    # print(f'Seed: {r}')
    NUMBER_GEN = 100
    ##################################

    solver = Solver(eternity_puzzle)
    best_solution = None 
    min_conflicts = 100000
    for _ in range(NUMBER_GEN):
        solver._build_greedy()
        conflicts = solver._get_conflicts()
        if conflicts < min_conflicts:
            best_solution = solver.solution
            min_conflicts = conflicts

    return best_solution, eternity_puzzle.get_total_n_conflict(best_solution)

class Solver:
    def __init__(self, eternity_puzzle: EternityPuzzle):
        self.puzzle = eternity_puzzle
        self.number_piece = eternity_puzzle.n_piece
        self.size = eternity_puzzle.board_size
        self.pieces = eternity_puzzle.piece_list

        self.solution = [0 for _ in range(self.number_piece)]

        self.all_index = [i for i in range(self.number_piece)]
        self.spiral_index = self._get_spiral()
        self.corner_index = [0, self.size-1, self.number_piece-self.size, self.number_piece-1]
        self.border_index = [i for i in range(1,self.size-1)] + [i for i in range(self.number_piece-self.size+1, self.number_piece-1)] + [i*self.size for i in range(1, self.size-1)] + [(i+1)*self.size-1 for i in range(1, self.size-1)]
        self.inner_index = list((set(self.all_index).difference(set(self.corner_index))).difference(set(self.border_index)))
        
    def _get_conflicts(self):
        return self.puzzle.get_total_n_conflict(self.solution)

    def _get_spiral(self):
        bot = 0
        top = self.size - 1
        left = 0
        right = self.size - 1
        res = []

        while bot <= top and left <= right:
            for col in range(left, right + 1):
                res.append(self.size * bot + col)
            bot += 1

            for row in range(bot, top+1):
                res.append(self.size * row + right)
            right -= 1

            if bot <= top:
                for col in range(right, left - 1, -1):
                    res.append(self.size * top + col)
                top -= 1

            if left <= right:
                for row in range(top, bot - 1, -1):
                    res.append(self.size * row + left)
                left += 1

        return res
    # Compte les conflits pour une certaine piece dans le puzzle avec une certaine solution
    def _count_conflict(self, position: int):
        i = position % self.size
        j = position // self.size
        num_conflict = 0
        if i > 0 and self.solution[self.size*j + (i-1)] != 0:
            if self.solution[position][WEST] != self.solution[self.size*j + (i-1)][EAST]:
                # print('Conflict A')
                num_conflict += 1
        if i < self.size-1 and self.solution[self.size*j + (i+1)] != 0:
            if self.solution[position][EAST] != self.solution[self.size*j + (i+1)][WEST]:
                # print('Conflict B')
                num_conflict += 1
        if j > 0 and self.solution[self.size*(j-1) + i] != 0:
            if self.solution[position][SOUTH] != self.solution[self.size*(j-1) + i][NORTH]:
                # print('Conflict C')
                num_conflict += 1
        if j < self.size-1 and self.solution[self.size*(j+1) + i] != 0:
            if self.solution[position][NORTH] != self.solution[self.size*(j+1) + i][SOUTH]:
                # print('Conflict D')
                num_conflict += 1
        nb_gray = self.solution[position].count(GRAY)
        if nb_gray == 1:
            if i == 0:
                if self.solution[position][WEST] != GRAY:
                    # print('Conflict A+')
                    num_conflict += 1
            if i == self.size-1:
                if self.solution[position][EAST] != GRAY:
                    # print('Conflict B+')
                    num_conflict += 1
            if j == 0:
                if self.solution[position][SOUTH] != GRAY:
                    # print('Conflict C+')
                    num_conflict += 1
            if j == self.size-1:
                if self.solution[position][NORTH] != GRAY:
                    # print('Conflict D+')
                    num_conflict += 1
        if nb_gray == 2:
            if i == 0 and j == 0:
                if self.solution[position][WEST] != GRAY:
                    num_conflict += 1
                if self.solution[position][SOUTH] != GRAY:
                    num_conflict += 1
            if i == self.size-1 and j == 0:
                if self.solution[position][EAST] != GRAY:
                    num_conflict += 1
                if self.solution[position][SOUTH] != GRAY:
                    num_conflict += 1
            if i == self.size-1 and j == self.size-1:
                if self.solution[position][EAST] != GRAY:
                    num_conflict += 1
                if self.solution[position][NORTH] != GRAY:
                    num_conflict += 1
            if i == 0 and j == self.size-1:
                if self.solution[position][WEST] != GRAY:
                    num_conflict += 1
                if self.solution[position][NORTH] != GRAY:
                    num_conflict += 1
        return num_conflict

    def _build_greedy(self):
        self.solution = [0 for _ in range(self.number_piece)]

        corner_pieces = [] 
        border_pieces = [] 
        inner_pieces  = []

        # Separation des pièces en 3 categories
        for piece in self.pieces:
            nb_gray = piece.count(GRAY)
            if nb_gray == 2:
                corner_pieces.append(piece)
            elif nb_gray == 1:
                border_pieces.append(piece)
            else:
                inner_pieces.append(piece)

        # Placement des coins et orientation
        index_corner = 0
        random.shuffle(corner_pieces)
        for k in self.corner_index:
            self.solution[k] = corner_pieces[index_corner]
            if k == self.corner_index[0]:
                while (self.solution[k][SOUTH] != GRAY or self.solution[k][WEST] != GRAY):
                    self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]

            if k == self.corner_index[1]:
                while (self.solution[k][SOUTH] != GRAY or self.solution[k][EAST] != GRAY):
                    self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]

            if k == self.corner_index[2]:
                while (self.solution[k][NORTH] != GRAY or self.solution[k][WEST] != GRAY):
                    self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]

            if k == self.corner_index[3]:
                while (self.solution[k][NORTH] != GRAY or self.solution[k][EAST] != GRAY):
                    self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]
            index_corner += 1

        # Placement des bordures et orientation en minimisant les conflits
        index_visited = []
        random.shuffle(border_pieces)
        for k in self.border_index:
            index_best = None
            best_orientation = None
            min_conflict = 4
            for b in range(len(border_pieces)):
                if b not in index_visited:
                    i = k % self.puzzle.board_size
                    j = k // self.puzzle.board_size
                    r = 0
                    self.solution[k] = border_pieces[b]
                    if j == 0:
                        while (self.solution[k][SOUTH] != GRAY):
                            r += 1
                            self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]
                    elif j == self.puzzle.board_size-1:
                        while (self.solution[k][NORTH] != GRAY):
                            r += 1
                            self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]
                    elif i == 0:
                        while (self.solution[k][WEST] != GRAY):
                            r += 1
                            self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]
                    elif i == self.puzzle.board_size-1:
                        while (self.solution[k][EAST] != GRAY):
                            r += 1
                            self.solution[k] = self.puzzle.generate_rotation(self.solution[k])[1]

                    if index_best == None:
                        index_best = b
                        best_orientation = r
                    conflicts = self._count_conflict(k)
                    if conflicts < min_conflict:
                        min_conflict = conflicts
                        index_best = b
                        best_orientation = r
            self.solution[k] = self.puzzle.generate_rotation(border_pieces[index_best])[best_orientation]
            index_visited.append(index_best)

        # Placement des pieces internes et orientation en minimisant les conflits
        index_visited = []
        random.shuffle(inner_pieces)
        for k in self.inner_index:
            index_best = None
            best_orientation = None
            min_conflict = 4
            for i in range(len(inner_pieces)):
                if i not in index_visited:
                    rotations = [0, 1, 2, 3]
                    random.shuffle(rotations)
                    for r in range(4):
                        if index_best == None:
                            index_best = i 
                            best_orientation = r
                        self.solution[k] = self.puzzle.generate_rotation(inner_pieces[i])[r]
                        conflicts = self._count_conflict(k)
                        if conflicts < min_conflict:
                            min_conflict = conflicts
                            index_best = i 
                            best_orientation = r
            self.solution[k] = self.puzzle.generate_rotation(inner_pieces[index_best])[best_orientation]
            index_visited.append(index_best)
