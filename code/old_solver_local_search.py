import copy 
import random 
import time 
from math import exp 
from old_solver_heuristic import get_spiral
#####################
# Constantes Pieces #
#####################
GRAY = 0
BLACK = 23
RED = 24
WHITE = 25

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3
############################
# Configuration Algorithme #
############################
NUMBER_RESTARTS = 50
TABU_LIST = []
MAX_TABU_SIZE = 350
TEMP = 25 
TEMP_F = 0.5
COOLING_FACTOR = 0.95
###################
# Classe Solution #
###################
class MySolution:
    def __init__(self, eternity_puzzle, sol, tabu_list=[], max_tabu_size=MAX_TABU_SIZE):
        self.__eternity_puzzle = eternity_puzzle
        self.__sol = sol 
        self.__tabu_list = tabu_list
        self.__tabu_size = max_tabu_size

        # Separation des pieces
        self.all_index = [i for i in range(eternity_puzzle.n_piece)]
        self.spiral_index = get_spiral(eternity_puzzle)
        self.corner_index = [0, eternity_puzzle.board_size-1, eternity_puzzle.n_piece-eternity_puzzle.board_size, eternity_puzzle.n_piece-1]
        self.border_index = [i for i in range(1,eternity_puzzle.board_size-1)] + [i for i in range(eternity_puzzle.n_piece-eternity_puzzle.board_size+1, eternity_puzzle.n_piece-1)] + [i*eternity_puzzle.board_size for i in range(1, eternity_puzzle.board_size-1)] + [(i+1)*eternity_puzzle.board_size-1 for i in range(1, eternity_puzzle.board_size-1)]
        self.inner_index = list((set(self.all_index).difference(set(self.corner_index))).difference(set(self.border_index)))
        self.__piece2conflict, self.__conflict2piece = self.generate_conflicts()

    def get_puzzle(self):
        return self.__eternity_puzzle
    def get_sol(self):
        return self.__sol
    def get_piece2conflict(self):
        return self.__piece2conflict
    def get_conflict2piece(self):
        return self.__conflict2piece
    def get_tabu(self):
        return self.__tabu_list
    def add_tabu(self, elem):
        self.__tabu_list.append(elem)
    def clear_tabu(self):
        while len(self.__tabu_list) > self.__tabu_size:
            self.__tabu_list.pop(0)
    def reset_tabu(self):
        self.__tabu_list = []
    def generate_conflicts(self):
        piece2conflict = {i: 0 for i in range(self.__eternity_puzzle.n_piece)}
        conflict2piece = {k: [] for k in range(5)}
        for k in self.all_index:
            piece2conflict[k] = count_conflict(self, k)
            conflict2piece[count_conflict(self, k)].append(k)
        return piece2conflict, conflict2piece

# Commpte le nombre de conflits pour une piece a la position k dans le puzzle
def count_conflict(solution: MySolution, k: int) -> int:
    puzzle = solution.get_puzzle()
    i = k % puzzle.board_size
    j = k // puzzle.board_size
    sol = solution.get_sol()
    num_conflict = 0
    if sol[k] == 0:
        return num_conflict
    if i > 0 and sol[puzzle.board_size*j + (i-1)] != 0:
        if sol[k][WEST] != sol[puzzle.board_size*j + (i-1)][EAST]:
            num_conflict += 1
    if i < puzzle.board_size-1 and sol[puzzle.board_size*j + (i+1)] != 0:
        if sol[k][EAST] != sol[puzzle.board_size*j + (i+1)][WEST]:
            num_conflict += 1
    if j > 0 and sol[puzzle.board_size*(j-1) + i] != 0:
        if sol[k][SOUTH] != sol[puzzle.board_size*(j-1) + i][NORTH]:
            num_conflict += 1
    if j < puzzle.board_size-1 and sol[puzzle.board_size*(j+1) + i] != 0:
        if sol[k][NORTH] != sol[puzzle.board_size*(j+1) + i][SOUTH]:
            num_conflict += 1
    nb_gray = sol[k].count(GRAY)
    if nb_gray == 1:
        if i == 0:
            if sol[k][WEST] != GRAY:
                num_conflict += 1
        if i == puzzle.board_size-1:
            if sol[k][EAST] != GRAY:
                num_conflict += 1
        if j == 0:
            if sol[k][SOUTH] != GRAY:
                num_conflict += 1
        if j == puzzle.board_size-1:
            if sol[k][NORTH] != GRAY:
                num_conflict += 1
    if nb_gray == 2:
        if i == 0 and j == 0:
            if sol[k][WEST] != GRAY:
                num_conflict += 1
            if sol[k][SOUTH] != GRAY:
                num_conflict += 1
        if i == puzzle.board_size-1 and j == 0:
            if sol[k][EAST] != GRAY:
                num_conflict += 1
            if sol[k][SOUTH] != GRAY:
                num_conflict += 1
        if i == puzzle.board_size-1 and j == puzzle.board_size-1:
            if sol[k][EAST] != GRAY:
                num_conflict += 1
            if sol[k][NORTH] != GRAY:
                num_conflict += 1
        if i == 0 and j == puzzle.board_size-1:
            if sol[k][WEST] != GRAY:
                num_conflict += 1
            if sol[k][NORTH] != GRAY:
                num_conflict += 1
    return num_conflict

# Compte le nombre total de conflits entre les pieces du bord et seulement les pieces du bord 
def conflicts_on_border(solution: MySolution) -> int:
    temp_sol = [0]*solution.get_puzzle().n_piece
    tot_conflicts = 0
    for i in range(4*solution.get_puzzle().board_size-4):
        temp_sol[solution.spiral_index[i]] = solution.get_sol()[solution.spiral_index[i]]
    temp_sol = MySolution(solution.get_puzzle(), temp_sol)
    for i in range(4*solution.get_puzzle().board_size-4):
        tot_conflicts += count_conflict(temp_sol, temp_sol.spiral_index[i])
    return tot_conflicts
####################
### NEIGHBORHOOD ###
####################
# Tourne chaque piece pour trouver une meilleure configuration 
# 3(n-2)^2 si on ne regarde que l'interieur
# n^2 si on regarde toutes les pieces '
# type_piece: 0 -> inner; 1 -> border; 2 -> all 
def rotate_inner(solution: MySolution, greedy=False, is_tabu=True, type_piece=0):
    eternity_puzzle = solution.get_puzzle()
    sol = solution.get_sol()
    sol_conflicts = eternity_puzzle.get_total_n_conflict(sol)

    match type_piece:
        case 0:
            indices = solution.inner_index
        case 1:
            indices = solution.corner_index + solution.border_index
        case 2:
            indices = solution.all_index

    best_rotation = None 
    best_piece = None 
    best_change = 0
    num_conflict = 4
    while num_conflict >= 0:
        for piece in solution.get_conflict2piece()[num_conflict]:
            if piece in indices:
                rotations = eternity_puzzle.generate_rotation(sol[piece])
                for r in range(1, len(rotations)):
                    sol[piece] = rotations[r]
                    conflicts = count_conflict(solution, piece)
                    if conflicts - num_conflict < best_change:
                        if (not is_tabu) or ((piece, r, sol_conflicts)):
                            best_change = conflicts - num_conflict
                            best_rotation = r
                            best_piece = piece 
                            if greedy:
                                sol[piece] = rotations[0]
                                if is_tabu:
                                    solution.add_tabu((best_piece, best_rotation, sol_conflicts))
                                sol[best_piece] = eternity_puzzle.generate_rotation(sol[best_piece])[best_rotation]
                                solution.generate_conflicts()
                                return solution, best_change

                sol[piece] = rotations[0]
        num_conflict -= 1

    if best_change != 0:
        if is_tabu:
            solution.add_tabu((best_piece, best_rotation, sol_conflicts))
        sol[best_piece] = eternity_puzzle.generate_rotation(sol[best_piece])[best_rotation]
        solution.generate_conflicts()

    return solution, best_change

# Tente d'echanger avec rotations toutes les paires de pieces homogenes = meme type (corner avec corner, inner avec inner, border avec border)
# 16(n-2)^4 si on ne regarde que l'interieur 
def swap_2(solution: MySolution, greedy=False, is_tabu=True, inner=True, random_swap=False, altering=False):
    eternity_puzzle = solution.get_puzzle()
    sol = solution.get_sol()
    if is_tabu:
        if not inner:
            sol_conflicts = conflicts_on_border(solution)
        else:
            sol_conflicts = eternity_puzzle.get_total_n_conflict(sol)

    # On garde une trace de la meilleure nouvelle configuration trouvee
    best_piece_a = None 
    best_rot_a = None
    best_piece_b = None
    best_rot_b = None  
    best_change = 0 
    num_conflict = 4 

    # On garde egalement une trace de la meilleure configuration alternative dans le cas ou aucune amelioration n'est trouvee
    best_alter_a = None
    best_alter_rot_a = None 
    best_alter_b = None 
    best_alter_rot_b = None 
    best_alter_change = 42

    if inner:
        indices = solution.inner_index
    else:
        indices = solution.corner_index + solution.border_index

    if random_swap:
        if inner:
            piece_a = 0
            piece_b = 0
            while piece_a == piece_b:
                piece_a = random.choice(indices)
                piece_b = random.choice(indices)
                r_a = random.choice([0, 1, 2, 3])
                r_b = random.choice([0, 1, 2, 3])
            temp = sol[piece_a]
            sol[piece_a] = eternity_puzzle.generate_rotation(sol[piece_b])[r_a]
            sol[piece_b] = eternity_puzzle.generate_rotation(temp)[r_b]
            solution.generate_conflicts()
            return solution, best_change
        else:
            piece_a = 0
            piece_b = 0
            while piece_a == piece_b or (piece_a in solution.border_index and piece_b in solution.corner_index) or (piece_a in solution.corner_index and piece_b in solution.border_index):
                piece_a = random.choice(indices)
                piece_b = random.choice(indices)
                r_a = random.choice([0, 1, 2, 3])
                r_b = random.choice([0, 1, 2, 3])
            temp = sol[piece_a]
            sol[piece_a] = eternity_puzzle.generate_rotation(sol[piece_b])[r_a]
            sol[piece_b] = eternity_puzzle.generate_rotation(temp)[r_b]
            solution.generate_conflicts()
            return solution, best_change

    while num_conflict >= 0 :
        for piece_a in solution.get_conflict2piece()[num_conflict]:
            temp_a = sol[piece_a]
            if piece_a in indices:
                for piece_b in indices:
                    if piece_a != piece_b:
                        if inner or ((piece_a in solution.corner_index and piece_b in solution.corner_index) or (piece_a in solution.border_index and piece_b in solution.border_index)):
                            # Compte les conflits impliquant ces 2 pieces en retirant les doublons 
                            curr_conflict_a = count_conflict(solution, piece_a)
                            curr_conflict_b = count_conflict(solution, piece_b) 
                            curr_conflicts = curr_conflict_a + curr_conflict_b
                            i_a = piece_a % eternity_puzzle.board_size
                            j_a = piece_a // eternity_puzzle.board_size
                            if i_a > 0 and piece_b == piece_a-1:
                                if sol[piece_b][EAST] != sol[piece_a][WEST]:
                                    curr_conflicts -= 1
                            elif i_a < eternity_puzzle.board_size-1 and piece_b == piece_a+1:
                                if sol[piece_b][WEST] != sol[piece_a][EAST]:
                                    curr_conflicts -= 1
                            elif j_a > 0 and piece_b == piece_a-eternity_puzzle.board_size:
                                if sol[piece_b][NORTH] != sol[piece_a][SOUTH]:
                                    curr_conflicts -= 1
                            elif j_a < eternity_puzzle.board_size-1 and piece_b == piece_a+eternity_puzzle.board_size:
                                if sol[piece_b][SOUTH] != sol[piece_a][NORTH]:
                                    curr_conflicts -= 1
                            temp_a = sol[piece_a]
                            temp_b = sol[piece_b]
                            for r_a in [0, 1, 2, 3]:
                                for r_b in [0, 1, 2, 3]:
                                    sol[piece_a] = eternity_puzzle.generate_rotation(temp_b)[r_a]
                                    sol[piece_b] = eternity_puzzle.generate_rotation(temp_a)[r_b]
                                    new_conflict_a = count_conflict(solution, piece_a)
                                    new_conflict_b = count_conflict(solution, piece_b)
                                    new_conflicts = new_conflict_a + new_conflict_b
                                    if i_a > 0 and piece_b == piece_a-1:
                                        if sol[piece_b][EAST] != sol[piece_a][WEST]:
                                            new_conflicts -= 1
                                    elif i_a < eternity_puzzle.board_size-1 and piece_b == piece_a+1:
                                        if sol[piece_b][WEST] != sol[piece_a][EAST]:
                                            new_conflicts -= 1
                                    elif j_a > 0 and piece_b == piece_a-eternity_puzzle.board_size:
                                        if sol[piece_b][NORTH] != sol[piece_a][SOUTH]:
                                            new_conflicts -= 1
                                    elif j_a < eternity_puzzle.board_size-1 and piece_b == piece_a+eternity_puzzle.board_size:
                                        if sol[piece_b][SOUTH] != sol[piece_a][NORTH]:
                                            new_conflicts -= 1
                                    if new_conflicts - curr_conflicts < best_change:
                                        if (not is_tabu) or ((piece_a, r_a, piece_b, r_b, sol_conflicts) not in solution.get_tabu() and (piece_b, r_b, piece_a, r_a, sol_conflicts) not in solution.get_tabu()):
                                            best_change = new_conflicts - curr_conflicts
                                            best_piece_a = piece_a
                                            best_piece_b = piece_b
                                            best_rot_a = r_a 
                                            best_rot_b = r_b
                                            if greedy:
                                                sol[piece_b] = temp_b
                                                sol[piece_a] = temp_a
                                                if is_tabu:
                                                    solution.add_tabu((best_piece_a, best_rot_a, best_piece_b, best_rot_b, sol_conflicts))
                                                temp = sol[best_piece_a]
                                                sol[best_piece_a] = eternity_puzzle.generate_rotation(sol[best_piece_b])[best_rot_a]
                                                sol[best_piece_b] = eternity_puzzle.generate_rotation(temp)[best_rot_b]
                                                solution.generate_conflicts()
                                                return solution, best_change


                                    if (new_conflicts - curr_conflicts < best_alter_change) :
                                        if (not is_tabu) or ((piece_a, r_a, piece_b, r_b, sol_conflicts) not in solution.get_tabu() and (piece_b, r_b, piece_a, r_a, sol_conflicts) not in solution.get_tabu()):
                                            best_alter_change = new_conflicts - curr_conflicts
                                            best_alter_a = piece_a
                                            best_alter_b = piece_b
                                            best_alter_rot_a = r_a 
                                            best_alter_rot_b = r_b 
                            sol[piece_b] = temp_b
                            sol[piece_a] = temp_a
        num_conflict -= 1
    
    if best_change != 0:
        if is_tabu:
            solution.add_tabu((best_piece_a, best_rot_a, best_piece_b, best_rot_b, sol_conflicts))
        temp = sol[best_piece_a]
        sol[best_piece_a] = eternity_puzzle.generate_rotation(sol[best_piece_b])[best_rot_a]
        sol[best_piece_b] = eternity_puzzle.generate_rotation(temp)[best_rot_b]
        solution.generate_conflicts()
    
    else:
        if altering and best_alter_change != 42:
            if is_tabu:
                solution.add_tabu((best_alter_a, best_alter_rot_a, best_alter_b, best_alter_rot_b, sol_conflicts))
            temp = sol[best_alter_a]
            sol[best_alter_a] = eternity_puzzle.generate_rotation(sol[best_alter_b])[best_alter_rot_a]
            sol[best_alter_b] = eternity_puzzle.generate_rotation(temp)[best_alter_rot_b]
            solution.generate_conflicts()
            return solution, best_alter_change

    return solution, best_change
########################
### Initial Solution ###
########################
def build_greedy(eternity_puzzle):
    solution = [0]*eternity_puzzle.n_piece
    sol = MySolution(eternity_puzzle, solution)

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
    for k in sol.corner_index:
        solution[k] = corner_pieces[index_corner]
        if k == sol.corner_index[0]:
            while (solution[k][SOUTH] != GRAY or solution[k][WEST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
        if k == sol.corner_index[1]:
            while (solution[k][SOUTH] != GRAY or solution[k][EAST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]

        if k == sol.corner_index[2]:
            while (solution[k][NORTH] != GRAY or solution[k][WEST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]

        if k == sol.corner_index[3]:
            while (solution[k][NORTH] != GRAY or solution[k][EAST] != GRAY):
                solution[k] = eternity_puzzle.generate_rotation(solution[k])[1]
        index_corner += 1

    # Placement des bordures et orientation en minimisant les conflits
    index_visited = []
    random.shuffle(border_pieces)
    for k in sol.all_index:
        if k in sol.border_index:
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
                    if count_conflict(sol, k) < min_conflict:
                        min_conflict = count_conflict(sol, k)
                        index_best = b
                        best_orientation = r
            solution[k] = eternity_puzzle.generate_rotation(border_pieces[index_best])[best_orientation]
            index_visited.append(index_best)

    # Placement des pieces internes et orientation en minimisant les conflits
    index_visited = []
    random.shuffle(inner_pieces)
    for k in sol.all_index:
        if k in sol.inner_index:
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
                        if count_conflict(sol, k) < min_conflict:
                            min_conflict = count_conflict(sol, k)
                            index_best = i 
                            best_orientation = r
            solution[k] = eternity_puzzle.generate_rotation(inner_pieces[index_best])[best_orientation]
            index_visited.append(index_best)

    return MySolution(eternity_puzzle, solution)
##############
### SOLVER ###
##############
def solve_local_search(eternity_puzzle, r=random.random()):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    ##################
    # Configuration
    ##################
    r = random.random()
    r = 0.18062110343039572
    # r = 0.33217689272656814
    # r = 0.4859014510305725
    # r = 0.8558517656282051
    # r = 0.604053790924224
    print(f'Seed: {r}')
    random.seed(r)      
    ##################
    sol_init = None
    min_conflicts = 100000
    # Some restarts to get a good initial solution
    for _ in range(NUMBER_RESTARTS):
        solution = build_greedy(eternity_puzzle)
        conflicts = eternity_puzzle.get_total_n_conflict(solution.get_sol())
        if conflicts < min_conflicts:
            sol_init = MySolution(eternity_puzzle, copy.deepcopy(solution.get_sol()))
            min_conflicts = conflicts

    # # Swap until local or global minima
    # conflicts = eternity_puzzle.get_total_n_conflict(sol_init.get_sol())
    # if conflicts == 0:
    #     return sol_init.get_sol(), eternity_puzzle.get_total_n_conflict(sol_init.get_sol())
    # change = -1
    # while conflicts != 0 and change != 0 :
    #     sol_rot, change_rot = rotate_inner(sol_init)
    #     sol_swap, change_swap = swap_2(sol_init)
    #     sol_swap_inner, change_inner = swap_2(sol_init, True, False)
    #     if change_rot < change_swap and change_rot < change_inner:
    #         sol_init = MySolution(eternity_puzzle, copy.deepcopy(sol_rot.get_sol()))
    #         change = change_rot
    #     elif change_swap < change_rot and change_swap < change_inner:
    #         sol_init = MySolution(eternity_puzzle, copy.deepcopy(sol_swap.get_sol()))
    #         change = change_swap
    #     elif change_inner <= change_rot and change_inner <= change_swap: 
    #         sol_init = MySolution(eternity_puzzle, copy.deepcopy(sol_swap_inner.get_sol()))
    #         change = change_inner
    #     conflicts += change
    # sol_init = MySolution(eternity_puzzle, copy.deepcopy(sol_init.get_sol()))

    # # Simulated Annealing + Tabu Search
    # best_sol = MySolution(eternity_puzzle, copy.deepcopy(sol_init.get_sol()))
    # best_conflicts = eternity_puzzle.get_total_n_conflict(best_sol.get_sol())
    # curr_sol = MySolution(eternity_puzzle, copy.deepcopy(sol_init.get_sol()))
    # curr_conflicts = best_conflicts
    # temp = TEMP
    # bad_count = 0
    # max_bad = 10
    # start_time = time.time()
    # while best_conflicts != 0 and (time.time() - start_time) <= 6000 and temp >= TEMP_F:
    #     if bad_count < max_bad:
    #         bad_count += 1
    #         new_sol = MySolution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()), copy.deepcopy(curr_sol.get_tabu()))
    #     else:
    #         bad_count = 0
    #         new_sol = MySolution(eternity_puzzle, copy.deepcopy(best_sol.get_sol()), copy.deepcopy(best_sol.get_tabu()))

    #     number_swap_inner = random.randint(eternity_puzzle.board_size, eternity_puzzle.board_size**2)
    #     while number_swap_inner > 0:
    #         new_sol, _ = swap_2(new_sol, greedy=False, is_tabu=False, inner=True, random_swap=False, altering=True)
    #         number_swap_inner -= 1
    #     number_swap_border = random.randint(3, 7)
    #     while number_swap_border > 0:
    #         new_sol, _ = swap_2(new_sol, greedy=False, is_tabu=False, inner=False, random_swap=False, altering=True)
    #         number_swap_border -= 1
    #     change = -1 
    #     conflicts = eternity_puzzle.get_total_n_conflict(new_sol.get_sol())
    #     new_sol.clear_tabu()

    #     max_iterations = 100
    #     iteration = 1
    #     while conflicts != 0 and change != 0 and iteration <= max_iterations:
    #         iteration += 1
    #         new_sol, change_rot = rotate_inner(new_sol)
    #         new_sol, change_swap = swap_2(new_sol, greedy=True, is_tabu=True, inner=True)
    #         new_sol, change_swap_2 = swap_2(new_sol, greedy=True, is_tabu=True, inner=False)
    #         new_sol.clear_tabu()
    #         change = change_rot + change_swap + change_swap_2 
    #         conflicts = eternity_puzzle.get_total_n_conflict(new_sol.get_sol())
    #     delta = curr_conflicts - conflicts
    #     proba_selection = random.uniform(0, 1)
    #     if delta >= 0:
    #         bad_count = 0
    #         curr_sol = MySolution(eternity_puzzle, copy.deepcopy(new_sol.get_sol()), copy.deepcopy(new_sol.get_tabu()))
    #         curr_conflicts = conflicts
    #     elif (delta < 0) or (proba_selection <= exp((-delta)/temp)):
    #         curr_sol = MySolution(eternity_puzzle, copy.deepcopy(new_sol.get_sol()), copy.deepcopy(new_sol.get_tabu()))
    #         curr_conflicts = conflicts
    #     if curr_conflicts < best_conflicts:
    #         bad_count = 0
    #         # print(f'Better')
    #         # print(f'{curr_conflicts}')
    #         best_sol = MySolution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()), copy.deepcopy(curr_sol.get_tabu()))
    #         best_conflicts = curr_conflicts
    #         # print(conflicts_on_border(best_sol))
    #         # return best_sol.get_sol(), eternity_puzzle.get_total_n_conflict(best_sol.get_sol())
        
    #     temp = COOLING_FACTOR*temp 
    
    # Simulated Annealing + Tabu Search V2
    best_sol = MySolution(eternity_puzzle, copy.deepcopy(sol_init.get_sol()))
    best_conflicts = eternity_puzzle.get_total_n_conflict(best_sol.get_sol())
    curr_sol = MySolution(eternity_puzzle, copy.deepcopy(sol_init.get_sol()))
    curr_conflicts = best_conflicts
    temp = TEMP
    max_before_swap_border = 10
    before_swap = 0
    start_time = time.time()
    while best_conflicts != 0 and (time.time() - start_time) <= 6000 and temp >= TEMP_F:
        new_sol = MySolution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()), TABU_LIST)
        curr_conflicts = eternity_puzzle.get_total_n_conflict(new_sol.get_sol())
        if conflicts_on_border(new_sol) != 0:
            new_sol, _ = swap_2(new_sol, greedy=False, is_tabu=True, inner=False, random_swap=False, altering=False)
        else:
            if before_swap >= max_before_swap_border:
                before_swap = 0
                new_sol, _ = swap_2(new_sol, greedy=False, is_tabu=True, inner=False, random_swap=False, altering=True)
        new_sol, _ = swap_2(new_sol, greedy=False, is_tabu=True, inner=True, random_swap=False, altering=True)
        new_sol.clear_tabu()

        delta = curr_conflicts - eternity_puzzle.get_total_n_conflict(new_sol.get_sol())
        proba_selection = random.uniform(0, 1)
        if delta >= 0:
            curr_sol = MySolution(eternity_puzzle, copy.deepcopy(new_sol.get_sol()))
        elif (delta < 0) or (proba_selection <= exp((-delta)/temp)):
            curr_sol = MySolution(eternity_puzzle, copy.deepcopy(new_sol.get_sol()))
        if curr_conflicts < best_conflicts:
            best_sol = MySolution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()))
            best_conflicts = eternity_puzzle.get_total_n_conflict(curr_sol.get_sol())
        
        temp = COOLING_FACTOR*temp 
        before_swap += 1

    return best_sol.get_sol(), eternity_puzzle.get_total_n_conflict(best_sol.get_sol())
