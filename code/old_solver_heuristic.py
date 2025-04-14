import copy
import random 

GRAY = 0
BLACK = 23
RED = 24
WHITE = 25

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

# Genere les indices du puzzle en les parcourant sous forme d'une spirale. En partant du coin inferieur gauche
def get_spiral(eternity_puzzle):
    bot = 0
    top = eternity_puzzle.board_size - 1
    left = 0
    right = eternity_puzzle.board_size - 1
    res = []

    while bot <= top and left <= right:
        for col in range(left, right + 1):
            res.append(eternity_puzzle.board_size * bot + col)
        bot += 1

        for row in range(bot, top+1):
            res.append(eternity_puzzle.board_size * row + right)
        right -= 1

        if bot <= top:
            for col in range(right, left - 1, -1):
                res.append(eternity_puzzle.board_size * top + col)
            top -= 1

        if left <= right:
            for row in range(top, bot - 1, -1):
                res.append(eternity_puzzle.board_size * row + left)
            left += 1

    return res

# Compte les conflits pour une certaine piece dans le puzzle avec une certaine solution
def count_conflict(eternity_puzzle, solution, k: int) -> int:
    i = k % eternity_puzzle.board_size
    j = k // eternity_puzzle.board_size
    num_conflict = 0
    if i > 0 and solution[eternity_puzzle.board_size*j + (i-1)] != 0:
        if solution[k][WEST] != solution[eternity_puzzle.board_size*j + (i-1)][EAST]:
            # print('Conflict A')
            num_conflict += 1
    if i < eternity_puzzle.board_size-1 and solution[eternity_puzzle.board_size*j + (i+1)] != 0:
        if solution[k][EAST] != solution[eternity_puzzle.board_size*j + (i+1)][WEST]:
            # print('Conflict B')
            num_conflict += 1
    if j > 0 and solution[eternity_puzzle.board_size*(j-1) + i] != 0:
        if solution[k][SOUTH] != solution[eternity_puzzle.board_size*(j-1) + i][NORTH]:
            # print('Conflict C')
            num_conflict += 1
    if j < eternity_puzzle.board_size-1 and solution[eternity_puzzle.board_size*(j+1) + i] != 0:
        if solution[k][NORTH] != solution[eternity_puzzle.board_size*(j+1) + i][SOUTH]:
            # print('Conflict D')
            num_conflict += 1
    nb_gray = solution[k].count(GRAY)
    if nb_gray == 1:
        if i == 0:
            if solution[k][WEST] != GRAY:
                # print('Conflict A+')
                num_conflict += 1
        if i == eternity_puzzle.board_size-1:
            if solution[k][EAST] != GRAY:
                # print('Conflict B+')
                num_conflict += 1
        if j == 0:
            if solution[k][SOUTH] != GRAY:
                # print('Conflict C+')
                num_conflict += 1
        if j == eternity_puzzle.board_size-1:
            if solution[k][NORTH] != GRAY:
                # print('Conflict D+')
                num_conflict += 1
    if nb_gray == 2:
        if i == 0 and j == 0:
            if solution[k][WEST] != GRAY:
                num_conflict += 1
            if solution[k][SOUTH] != GRAY:
                num_conflict += 1
        if i == eternity_puzzle.board_size-1 and j == 0:
            if solution[k][EAST] != GRAY:
                num_conflict += 1
            if solution[k][SOUTH] != GRAY:
                num_conflict += 1
        if i == eternity_puzzle.board_size-1 and j == eternity_puzzle.board_size-1:
            if solution[k][EAST] != GRAY:
                num_conflict += 1
            if solution[k][NORTH] != GRAY:
                num_conflict += 1
        if i == 0 and j == eternity_puzzle.board_size-1:
            if solution[k][WEST] != GRAY:
                num_conflict += 1
            if solution[k][NORTH] != GRAY:
                num_conflict += 1
    return num_conflict

def generate_conflicts(eternity_puzzle, solution):
    all_index = [i for i in range(eternity_puzzle.n_piece)]
    piece2conflict = {i: 0 for i in range(eternity_puzzle.n_piece)}
    conflict2piece = {k: [] for k in range(5)}
    for k in all_index:
        piece2conflict[k] = count_conflict(eternity_puzzle, solution, k)
        conflict2piece[count_conflict(eternity_puzzle, solution, k)].append(k)
    return piece2conflict, conflict2piece

# Construit une solution initiale de maniere greedy
def build_greedy(eternity_puzzle):
    solution = [0]*eternity_puzzle.n_piece
    all_index = [i for i in range(eternity_puzzle.n_piece)]
    spiral_index = get_spiral(eternity_puzzle)
    corner_index = [0, eternity_puzzle.board_size-1, eternity_puzzle.n_piece-eternity_puzzle.board_size, eternity_puzzle.n_piece-1]
    border_index = [i for i in range(1,eternity_puzzle.board_size-1)] + [i for i in range(eternity_puzzle.n_piece-eternity_puzzle.board_size+1, eternity_puzzle.n_piece-1)] + [i*eternity_puzzle.board_size for i in range(1, eternity_puzzle.board_size-1)] + [(i+1)*eternity_puzzle.board_size-1 for i in range(1, eternity_puzzle.board_size-1)]
    inner_index = list((set(all_index).difference(set(corner_index))).difference(set(border_index)))

    corner_pieces = [] 
    border_pieces = [] 
    inner_pieces  = []

    # Separation des pièces en 3 categories
    for piece in eternity_puzzle.piece_list:
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
    for k in corner_index:
        solution[k] = corner_pieces[index_corner]
        if k == corner_index[0]:
            while (solution[k][SOUTH] != GRAY or solution[k][WEST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
        if k == corner_index[1]:
            while (solution[k][SOUTH] != GRAY or solution[k][EAST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]

        if k == corner_index[2]:
            while (solution[k][NORTH] != GRAY or solution[k][WEST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]

        if k == corner_index[3]:
            while (solution[k][NORTH] != GRAY or solution[k][EAST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
        index_corner += 1

    # Placement des bordures et orientation en minimisant les conflits
    index_visited = []
    random.shuffle(border_pieces)
    for k in all_index:
        if k in border_index:
            index_best = None
            best_orientation = None
            min_conflict = 4
            for b in range(len(border_pieces)):
                if b not in index_visited:
                    i = k % eternity_puzzle.board_size
                    j = k // eternity_puzzle.board_size
                    r = 0
                    solution[k] = border_pieces[b]
                    if j == 0:
                        while (solution[k][SOUTH] != GRAY):
                            r += 1
                            solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
                    elif j == eternity_puzzle.board_size-1:
                        while (solution[k][NORTH] != GRAY):
                            r += 1
                            solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
                    elif i == 0:
                        while (solution[k][WEST] != GRAY):
                            r += 1
                            solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
                    elif i == eternity_puzzle.board_size-1:
                        while (solution[k][EAST] != GRAY):
                            r += 1
                            solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]

                    if index_best == None:
                        index_best = b
                        best_orientation = r
                    if count_conflict(eternity_puzzle, solution, k) < min_conflict:
                        min_conflict = count_conflict(eternity_puzzle, solution, k)
                        index_best = b
                        best_orientation = r
            solution[k] = eternity_puzzle.generate_rotation(border_pieces[index_best])[best_orientation]
            index_visited.append(index_best)

    # Placement des pieces internes et orientation en minimisant les conflits
    index_visited = []
    random.shuffle(inner_pieces)
    for k in all_index:
        if k in inner_index:
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
                        solution[k] = eternity_puzzle.generate_rotation(inner_pieces[i])[r]
                        if count_conflict(eternity_puzzle, solution, k) < min_conflict:
                            min_conflict = count_conflict(eternity_puzzle, solution, k)
                            index_best = i 
                            best_orientation = r
            solution[k] = eternity_puzzle.generate_rotation(inner_pieces[index_best])[best_orientation]
            index_visited.append(index_best)

    piece2conflict, conflict2piece = generate_conflicts(eternity_puzzle, solution)

    return solution, eternity_puzzle.get_total_n_conflict(solution), piece2conflict, conflict2piece

def solve_heuristic(eternity_puzzle, r=random.random()):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    # r = random.random()
    r = 0.2332132132
    print(f'Seed: {r}')
    random.seed(r)
    NUMBER_GEN = 100
    best_solution = None 
    min_conflicts = 100000
    for _ in range(NUMBER_GEN):
        solution, conflicts, _, _ = build_greedy(eternity_puzzle)
        if conflicts < min_conflicts:
            best_solution = copy.deepcopy(solution)
            min_conflicts = conflicts

    return best_solution, eternity_puzzle.get_total_n_conflict(best_solution)