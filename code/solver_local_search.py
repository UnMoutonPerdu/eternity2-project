import copy 
import random 
import time 
from itertools import combinations, product
from math import exp 
from eternity_puzzle import EternityPuzzle
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
MAX_TABU_SIZE = 400
MAX_ITER_BEFORE_SWAP_BORDER = 10
MAX_TIME = 600
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
    #################
    # Configuration #
    #################
    r = 0.18062110343039572
    print(f'Seed: {r}')
    random.seed(r)      
    ##################
    # Initialisation de la solution
    solver = Solver(eternity_puzzle)
    best_init = None 
    min_conflicts = float('inf')
    for _ in range(NUMBER_RESTARTS):
        solver._build_greedy()
        conflicts = solver._get_conflicts()
        if conflicts < min_conflicts:
            best_init = solver.solution
            min_conflicts = conflicts
    solver.solution = best_init

    # Tabu Search
    best_sol = copy.deepcopy(solver.solution)
    best_score = solver._get_conflicts()
    nb_iter = 0
    start_time = time.time() 

    while best_score != 0 and (time.time() - start_time) <= MAX_TIME:
        if solver._count_conflict_border_only() != 0:
            swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=1, random_swap=False, altering=True)
            solver.tabu.append((swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts))
            solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)
        else:
            if nb_iter >= MAX_ITER_BEFORE_SWAP_BORDER:
                nb_iter = 0 
                swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=1, random_swap=False, altering=True)
                solver.tabu.append((swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts))
                solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)

        swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=0, random_swap=False, altering=True)
        solver.tabu.append((swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts))
        solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)

        while len(solver.tabu) > MAX_TABU_SIZE:
            solver.tabu.pop(0)
        
        if solver._get_conflicts() < best_score:
            best_score = solver._get_conflicts()
            best_sol = copy.deepcopy(solver.solution)
        
        nb_iter += 1

    return best_sol, best_score

#################
# Classe Solver #
#################
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

        self.tabu = []

    def _get_conflicts(self):
        return self.puzzle.get_total_n_conflict(self.solution)
    
    def _is_homogeneous(self, idx_piece_a, idx_piece_b):
        return self.solution[idx_piece_a].count(GRAY) == self.solution[idx_piece_b].count(GRAY)
    
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
    ###########################
    ### Gestion de conflits ###
    ###########################
    def _count_conflict(self, position: int, solution_temp=None, piece_temp=None):
        if solution_temp == None:
            solution = self.solution
        else:
            solution = solution_temp 
        if piece_temp == None:
            piece = solution[position]
        else:
            piece = piece_temp
        i = position % self.size
        j = position // self.size
        num_conflict = 0
        if i > 0 and solution[self.size*j + (i-1)] != 0:
            if piece[WEST] != solution[self.size*j + (i-1)][EAST]:
                num_conflict += 1
        if i < self.size-1 and solution[self.size*j + (i+1)] != 0:
            if piece[EAST] != solution[self.size*j + (i+1)][WEST]:
                num_conflict += 1
        if j > 0 and solution[self.size*(j-1) + i] != 0:
            if piece[SOUTH] != solution[self.size*(j-1) + i][NORTH]:
                num_conflict += 1
        if j < self.size-1 and solution[self.size*(j+1) + i] != 0:
            if piece[NORTH] != solution[self.size*(j+1) + i][SOUTH]:
                num_conflict += 1
        nb_gray = piece.count(GRAY)
        if nb_gray == 1:
            if i == 0:
                if piece[WEST] != GRAY:
                    num_conflict += 1
            if i == self.size-1:
                if piece[EAST] != GRAY:
                    num_conflict += 1
            if j == 0:
                if piece[SOUTH] != GRAY:
                    num_conflict += 1
            if j == self.size-1:
                if piece[NORTH] != GRAY:
                    num_conflict += 1
        if nb_gray == 2:
            if i == 0 and j == 0:
                if piece[WEST] != GRAY:
                    num_conflict += 1
                if piece[SOUTH] != GRAY:
                    num_conflict += 1
            if i == self.size-1 and j == 0:
                if piece[EAST] != GRAY:
                    num_conflict += 1
                if piece[SOUTH] != GRAY:
                    num_conflict += 1
            if i == self.size-1 and j == self.size-1:
                if piece[EAST] != GRAY:
                    num_conflict += 1
                if piece[NORTH] != GRAY:
                    num_conflict += 1
            if i == 0 and j == self.size-1:
                if piece[WEST] != GRAY:
                    num_conflict += 1
                if piece[NORTH] != GRAY:
                    num_conflict += 1
        return num_conflict

    def _count_conflict_border_only(self):
        temp_sol = [0 for _ in range(self.number_piece)]
        tot_conflicts = 0
        for i in range(4*self.size-4):
            temp_sol[self.spiral_index[i]] = self.solution[self.spiral_index[i]]
        for i in range(4*self.size-4):
            tot_conflicts += self._count_conflict(self.spiral_index[i], solution_temp=temp_sol)
        return tot_conflicts
    
    def _count_conflict_two_pieces(self, idx_piece_a, idx_piece_b):
        curr_conflict_a = self._count_conflict(idx_piece_a)
        curr_conflict_b = self._count_conflict(idx_piece_a) 
        curr_conflicts = curr_conflict_a + curr_conflict_b
        i_a = idx_piece_a % self.size
        j_a = idx_piece_a // self.size
        if i_a > 0 and idx_piece_b == idx_piece_a-1:
            if self.solution[idx_piece_b][EAST] != self.solution[idx_piece_a][WEST]:
                curr_conflicts -= 1
        elif i_a < self.size-1 and idx_piece_b == idx_piece_a+1:
            if self.solution[idx_piece_b][WEST] != self.solution[idx_piece_a][EAST]:
                curr_conflicts -= 1
        elif j_a > 0 and idx_piece_b == idx_piece_a-self.size:
            if self.solution[idx_piece_b][NORTH] != self.solution[idx_piece_a][SOUTH]:
                curr_conflicts -= 1
        elif j_a < self.size-1 and idx_piece_b == idx_piece_a+self.size:
            if self.solution[idx_piece_b][SOUTH] != self.solution[idx_piece_a][NORTH]:
                curr_conflicts -= 1
        return curr_conflicts
    #########################
    ### Solution initiale ###
    #########################
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
    ####################
    ### NEIGHBORHOOD ###
    ####################
    # Tourne chaque piece pour trouver une meilleure configuration 
    # 3(n-2)^2 si on ne regarde que l'interieur
    # n^2 si on regarde toutes les pieces '
    # type_piece: 0 -> inner; 1 -> border; 2 -> all 
    def _rotate_neigh(self, greedy=False, is_tabu=True, type_piece=0):
        match type_piece:
            case 0:
                indices = self.inner_index
            case 1:
                indices = self.corner_index + self.border_index
            case 2:
                indices = self.all_index

        best_rotation = None 
        best_piece = None 
        best_change = 0
        best_curr = 0
        # On regarde les pieces de la plus conflictuelle a la moins conflictuelle
        conflicts_per_pieces = [(i, self._count_conflict(i)) for i in indices]
        random.shuffle(conflicts_per_pieces)
        conflicts_per_pieces.sort(key=lambda x: -x[1])
        conflicts_per_pieces = [i for (i, _) in conflicts_per_pieces]
        for idx_piece in conflicts_per_pieces:
            curr_conflicts = self._count_conflict(idx_piece)
            for r, new_piece in enumerate(self.puzzle.generate_rotation(self.solution[idx_piece])):
                change = self._count_conflict(idx_piece, piece_temp=new_piece) - curr_conflicts
                if change < best_change:
                    if (not is_tabu) or ((self.solution[idx_piece], r, curr_conflicts)) in self.tabu:
                        best_change = change 
                        best_rotation = r 
                        best_piece = idx_piece 
                        best_curr = curr_conflicts
                        if greedy:
                            return best_piece, best_rotation, best_curr, best_change
              
        return best_piece, best_rotation, best_curr, best_change

    # Tente d'echanger avec rotations toutes les paires de pieces homogenes = meme type (corner avec corner, inner avec inner, border avec border)
    # 16(n-2)^4 si on ne regarde que l'interieur 
    # type_piece: 0 -> inner; 1 -> border; 2 -> all 
    def _swap_2(self, greedy=False, is_tabu=True, type_piece=0, random_swap=False, altering=False):
        if is_tabu:
            if type_piece == 1:
                sol_conflicts = self._count_conflict_border_only()
            else:
                sol_conflicts = self._get_conflicts()
        else:
            sol_conflicts = self._get_conflicts()

        if type_piece == 0:
            indices = self.inner_index
        elif type_piece == 1:
            indices = self.corner_index + self.border_index
        else:
            indices = self.all_index

        random.shuffle(indices)
        if random_swap:
            if type_piece == 0:
                idx_piece_a, idx_piece_b = random.choice(combinations(indices), 2)
                r_a = random.choice([0, 1, 2, 3])
                r_b = random.choice([0, 1, 2, 3])
                return idx_piece_a, r_a, idx_piece_b, r_b, sol_conflicts, -1
            elif type_piece == 1:
                idx_piece_a, idx_piece_b = random.choice(combinations(indices), 2)
                while not self._is_homogeneous(idx_piece_a, idx_piece_b):
                    idx_piece_a, idx_piece_b = random.choice(combinations(indices), 2)
                nb_gray = self.solution[idx_piece_a].count(GRAY)
                r_a = 0
                r_b = 0
                rotations_a = self.puzzle.generate_rotation(self.solution[idx_piece_a])
                rotations_b = self.puzzle.generate_rotation(self.solution[idx_piece_b])
                if nb_gray == 1:
                    orientation_a = self.solution[idx_piece_a].index(GRAY)
                    orientation_b = self.solution[idx_piece_b].index(GRAY)
                    while rotations_a[r_a][orientation_b] != GRAY:
                        r_a += 1
                    while rotations_b[r_b][orientation_a] != GRAY:
                        r_b += 1
                elif nb_gray == 2:
                    orientation_a = [i for i, elem in enumerate(self.solution[idx_piece_a]) if elem == GRAY]
                    orientation_b = [i for i, elem in enumerate(self.solution[idx_piece_b]) if elem == GRAY]          
                    while rotations_a[r_a][orientation_b[0]] != GRAY or rotations_a[r_a][orientation_b[1]] != GRAY:
                        r_a += 1
                    while rotations_b[r_b][orientation_a[0]] != GRAY or rotations_b[r_b][orientation_a[1]] != GRAY:
                        r_b += 1
                return idx_piece_a, r_a, idx_piece_b, r_b, sol_conflicts, -1
            else:
                # Not implemented because never used. Inner or border always specified on random swaps
                pass

        # On garde une trace de la meilleure nouvelle configuration trouvee
        best_idx_piece_a = None 
        best_rot_a = None
        best_idx_piece_b = None
        best_rot_b = None  
        best_change = 0 
        num_conflict = 4 

        # On garde egalement une trace de la meilleure configuration alternative dans le cas ou aucune amelioration n'est trouvee
        best_alter_idx_a = None
        best_alter_rot_a = None 
        best_alter_idx_b = None 
        best_alter_rot_b = None 
        best_alter_change = 42

        # On regarde les pieces de la plus conflictuelle a la moins conflictuelle
        conflicts_per_pieces = [(i, self._count_conflict(i)) for i in indices]
        random.shuffle(conflicts_per_pieces)
        conflicts_per_pieces.sort(key=lambda x: -x[1])
        conflicts_per_pieces = [i for (i, _) in conflicts_per_pieces]
        for idx_piece_a, idx_piece_b in combinations(conflicts_per_pieces, 2):
            if self._is_homogeneous(idx_piece_a, idx_piece_b):
                curr_conflicts = self._count_conflict_two_pieces(idx_piece_a, idx_piece_b)
                temp_a = self.solution[idx_piece_a]
                temp_b = self.solution[idx_piece_b]
                for ((r_b, new_piece_a), (r_a, new_piece_b)) in product(enumerate(self.puzzle.generate_rotation(temp_a)), enumerate(self.puzzle.generate_rotation(temp_b))):
                    self.solution[idx_piece_a] = new_piece_b
                    self.solution[idx_piece_b] = new_piece_a
                    new_conflicts = self._count_conflict_two_pieces(idx_piece_a, idx_piece_b)
                    self.solution[idx_piece_a] = temp_a
                    self.solution[idx_piece_b] = temp_b
                    if new_conflicts - curr_conflicts < best_change:
                        if (not is_tabu) or ((idx_piece_a, r_a, idx_piece_b, r_b, sol_conflicts) not in self.tabu and (idx_piece_b, r_b, idx_piece_a, r_a, sol_conflicts) not in self.tabu):
                            best_change = new_conflicts - curr_conflicts
                            best_idx_piece_a = idx_piece_a
                            best_idx_piece_b = idx_piece_b
                            best_rot_a = r_a
                            best_rot_b = r_b 
                            if greedy:
                                return best_idx_piece_a, best_rot_a, best_idx_piece_b, best_rot_b, sol_conflicts, best_change
                    
                    elif altering and (new_conflicts - curr_conflicts < best_alter_change):
                        if (not is_tabu) or ((idx_piece_a, r_a, idx_piece_b, r_b, sol_conflicts) not in self.tabu and (idx_piece_b, r_b, idx_piece_a, r_a, sol_conflicts) not in self.tabu):
                            best_alter_change = new_conflicts - curr_conflicts
                            best_alter_idx_a = idx_piece_a
                            best_alter_idx_b = idx_piece_b
                            best_alter_rot_a = r_a 
                            best_alter_rot_b = r_b 

        if best_change != 0:
            return best_idx_piece_a, best_rot_a, best_idx_piece_b, best_rot_b, sol_conflicts, best_change
        else:
            if altering and best_alter_change != 42:
                return best_alter_idx_a, best_alter_rot_a, best_alter_idx_b, best_alter_rot_b, sol_conflicts, best_alter_change
            else:
                return None, None, None, None, None, 0
    
    def _do_swap_2(self, swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b):
        temp = self.solution[swap_BP_a]
        self.solution[swap_BP_a] = self.puzzle.generate_rotation(self.solution[swap_BP_b])[swap_BR_a]
        self.solution[swap_BP_b] = self.puzzle.generate_rotation(temp)[swap_BR_b]

