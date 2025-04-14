import copy 
import random 
import time 
from itertools import combinations, product
from math import exp, comb 
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
MAX_TABU_SIZE = 360
TEMP_0 = 100.0
TEMP_F = 0.05
COOLING_FACTOR = 0.99
MAX_ITER_1 = 400
MAX_ITER_2 = 400
MAX_ITER_3 = 3500
MAX_TIME_1 = 60
MAX_TIME_2 = 3600
BETA_1 = 0.5
BETA_2 = 6000
GAMMA = 0.5
GAMMA_BORDER = 0.2
##############
### SOLVER ###
##############
def solve_advanced(eternity_puzzle):
    """
    Your solver for the problem
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
    solver = Solver(eternity_puzzle)
    # Phase 1
    solver._phase_1()

    # Tabu Search after Phase 1 for borders + corners
    tot_conflicts = solver._count_conflict_border_only()
    start_tabu_phase_1 = time.time()
    iteration_1 = 0
    while tot_conflicts != 0 and (time.time() - start_tabu_phase_1) < MAX_TIME_1 and iteration_1 < MAX_ITER_1:
        iteration_1 += 1
        swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=1, random_swap=False, altering=True)
        if swap_BP_a != None:
            solver.tabu.append((solver.solution[swap_BP_a], swap_BR_a, solver.solution[swap_BP_b], swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
            solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)
        tot_conflicts = solver._count_conflict_border_only()
        solver._clear_tabu()
    
    # Phase 2
    solver._phase_2()
    
    # Tabu Search sur l'interieur 
    best_sol_overall = copy.deepcopy(solver.solution)
    best_score_overall = solver._get_conflicts()
    
    best_sol = copy.deepcopy(solver.solution)
    best_score = solver._get_conflicts()

    start_time = time.time()
    iteration_2 = 0 
    iteration_3 = 0
    solver.tabu = []
    while best_score_overall != 0 and (time.time() - start_time) < MAX_TIME_2:
        # print(f'Iteration without Improvements: {iteration_2}')
        rot_BP, rot_BR, rot_base_conflicts, rot_change = solver._rotate_neigh(greedy=False, is_tabu=True, type_piece=0)
        swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=2, random_swap=False, altering=True)

        if rot_change != 0 and rot_change < swap_change:
            solver.tabu.append((solver.solution[rot_BP], rot_BR, rot_base_conflicts))
            solver.solution[rot_BP] = solver.puzzle.generate_rotation(solver.solution[rot_BP])[rot_BR]
        else:
            solver.tabu.append((solver.solution[swap_BP_a], swap_BR_a, solver.solution[swap_BP_b], swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
            solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)

        solver._clear_tabu()
        new_conflicts = solver._get_conflicts()

        if new_conflicts < best_score:
            print(best_score)
            iteration_2 = 0
            iteration_3 = 0
            best_sol = copy.deepcopy(solver.solution)
            best_score = new_conflicts
            if best_score < best_score_overall:
                print(f'New Best Score Overall: {best_score}')
                best_sol_overall = copy.deepcopy(best_sol)
                best_score_overall = best_score
        else:
            iteration_2 += 1
            iteration_3 += 1

        # Reset init solution
        if iteration_3 >= MAX_ITER_3 and (time.time() - start_time) < MAX_TIME_2:
            print("SWAP SOL INIT")
            iteration_1 = 0
            iteration_2 = 0 
            iteration_3 = 0
            
            for _ in range(int(GAMMA_BORDER*GAMMA*eternity_puzzle.board_size**2)):
                swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=1, random_swap=True, altering=True)
                solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)

            for _ in range(int((1-GAMMA_BORDER)*GAMMA*eternity_puzzle.board_size**2)):
                swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=0, random_swap=True, altering=True)
                solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)

            solver.tabu = [] 
            # Tabu Search after Phase 1 for borders + corners
            tot_conflicts = solver._count_conflict_border_only()
            start_tabu_phase_1 = time.time()
            iteration_1 = 0
            while tot_conflicts != 0 and (time.time() - start_tabu_phase_1) < MAX_TIME_1 and iteration_1 < MAX_ITER_1:
                iteration_1 += 1
                swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=1, random_swap=False, altering=True)
                if swap_BP_a != None:
                    solver.tabu.append((solver.solution[swap_BP_a], swap_BR_a, solver.solution[swap_BP_b], swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
                    solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)
                tot_conflicts = solver._count_conflict_border_only()
                solver._clear_tabu()
            
            solver.tabu = [] 
            best_sol = copy.deepcopy(solver.solution)
            best_score = solver._get_conflicts()
            print("END SWAP SOL INIT")
        
        # SA to help with local minima if stuck 
        elif iteration_2 >= MAX_ITER_2 and (time.time() - start_time) < MAX_TIME_2:
            print("SIMULATED ANNEALING")
            iteration_2 = 0
            temperature = TEMP_0
            solver.tabu = [] 
            while temperature >= TEMP_F and (time.time() - start_time) < MAX_TIME_2:
                rot_BP, rot_BR, rot_base_conflicts, rot_change = solver._rotate_neigh(greedy=False, is_tabu=True, type_piece=0)
                swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = solver._swap_2(greedy=False, is_tabu=True, type_piece=2, random_swap=False, altering=True)
                if rot_change < 0 or swap_change < 0:
                    if rot_change != 0 and rot_change < swap_change:
                        solver.tabu = [] 
                        solver.tabu.append((rot_BP, rot_BR, rot_base_conflicts))
                        solver.solution[rot_BP] = solver.puzzle.generate_rotation(solver.solution[rot_BP])[rot_BR]
                    else:
                        solver.tabu = [] 
                        solver.tabu.append((swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
                        solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)
                else:
                    delta = swap_change
                    proba_selection = random.uniform(0, 1)
                    if proba_selection <= exp((-delta)/temperature):
                        solver.tabu = [] 
                        solver.tabu.append((swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
                        solver._do_swap_2(swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b)
                
                new_conflicts = solver._get_conflicts()
                if new_conflicts < best_score:
                    print("BETTER IN SA")
                    iteration_2 = 0
                    iteration_3 = 0
                    best_sol = copy.deepcopy(solver.solution)
                    best_score = new_conflicts
                    if best_score < best_score_overall:
                        print(f'New Best Score Overall: {best_score}')
                        best_sol_overall = copy.deepcopy(best_sol)
                        best_score_overall = best_score
        
                temperature = temperature*COOLING_FACTOR
            print("END SIMULATED ANNEALING")

    return best_sol_overall, best_score_overall

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
        self.homogenous_pieces = comb(4, 2) + comb(4*(eternity_puzzle.board_size-2), 2) + comb((eternity_puzzle.board_size-2)**2, 2)

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
    
    def _clear_tabu(self):
        while len(self.tabu) > MAX_TABU_SIZE:
            self.tabu.pop(0)
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
                # print('Conflict A')
                num_conflict += 1
        if i < self.size-1 and solution[self.size*j + (i+1)] != 0:
            if piece[EAST] != solution[self.size*j + (i+1)][WEST]:
                # print('Conflict B')
                num_conflict += 1
        if j > 0 and solution[self.size*(j-1) + i] != 0:
            if piece[SOUTH] != solution[self.size*(j-1) + i][NORTH]:
                # print('Conflict C')
                num_conflict += 1
        if j < self.size-1 and solution[self.size*(j+1) + i] != 0:
            if piece[NORTH] != solution[self.size*(j+1) + i][SOUTH]:
                # print('Conflict D')
                num_conflict += 1
        nb_gray = piece.count(GRAY)
        if nb_gray == 1:
            if i == 0:
                if piece[WEST] != GRAY:
                    # print('Conflict A+')
                    num_conflict += 1
            if i == self.size-1:
                if piece[EAST] != GRAY:
                    # print('Conflict B+')
                    num_conflict += 1
            if j == 0:
                if piece[SOUTH] != GRAY:
                    # print('Conflict C+')
                    num_conflict += 1
            if j == self.size-1:
                if piece[NORTH] != GRAY:
                    # print('Conflict D+')
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
        curr_conflict_b = self._count_conflict(idx_piece_b) 
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
    def _phase_1(self):
        solution = [0]*self.number_piece

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

    def _phase_2(self):
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

        sol_conflicts = self._get_conflicts()

        best_rotation = None 
        best_piece = None 
        best_change = 0
        # On regarde les pieces de la plus conflictuelle a la moins conflictuelle
        conflicts_per_pieces = [(i, self._count_conflict(i)) for i in indices]
        random.shuffle(conflicts_per_pieces)
        conflicts_per_pieces.sort(key=lambda x: -x[1])
        conflicts_per_pieces = [i for (i, _) in conflicts_per_pieces]
        for idx_piece in conflicts_per_pieces:
            curr_conflicts = self._count_conflict(idx_piece)
            for r, new_piece in enumerate(self.puzzle.generate_rotation(self.solution[idx_piece])):
                if r == 0:
                    continue
                change = self._count_conflict(idx_piece, piece_temp=new_piece) - curr_conflicts
                if change < best_change:
                    if (not is_tabu) or ((self.solution[idx_piece], r, sol_conflicts)) in self.tabu:
                        best_change = change 
                        best_rotation = r 
                        best_piece = idx_piece 
                        if greedy:
                            return best_piece, best_rotation, sol_conflicts, best_change
        
        return best_piece, best_rotation, sol_conflicts, best_change

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
                for a, b in combinations(indices, 2):
                    idx_piece_a = a 
                    idx_piece_b = b
                    break 
                r_a = random.choice([0, 1, 2, 3])
                r_b = random.choice([0, 1, 2, 3])
                return idx_piece_a, r_a, idx_piece_b, r_b, sol_conflicts, -1
            elif type_piece == 1:
                for a, b in combinations(indices, 2):
                    idx_piece_a = a 
                    idx_piece_b = b
                    if self._is_homogeneous(idx_piece_a, idx_piece_b):
                        break 
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

        # On garde egalement une trace de la meilleure configuration alternative dans le cas ou aucune amelioration n'est trouvee
        best_alter_idx_a = None
        best_alter_rot_a = None 
        best_alter_idx_b = None 
        best_alter_rot_b = None 
        best_alter_change = 42

        pairs_checked = 0
        for idx_piece_a, idx_piece_b in combinations(indices, 2):
            if pairs_checked >= max(BETA_1*self.homogenous_pieces, BETA_2):
                break 
            if self._is_homogeneous(idx_piece_a, idx_piece_b):
                pairs_checked += 1
                curr_conflicts = self._count_conflict_two_pieces(idx_piece_a, idx_piece_b)
                temp_a = self.solution[idx_piece_a]
                temp_b = self.solution[idx_piece_b]
                for ((r_b, new_piece_a), (r_a, new_piece_b)) in product(enumerate(self.puzzle.generate_rotation(temp_a)), enumerate(self.puzzle.generate_rotation(temp_b))):
                    self.solution[idx_piece_a] = new_piece_b
                    self.solution[idx_piece_b] = new_piece_a
                    new_conflicts = self._count_conflict_two_pieces(idx_piece_a, idx_piece_b)
                    self.solution[idx_piece_a] = temp_a
                    self.solution[idx_piece_b] = temp_b
                    if (sol_conflicts + new_conflicts - curr_conflicts) == 0:
                        best_change = new_conflicts - curr_conflicts
                        best_piece_a = idx_piece_a
                        best_piece_b = idx_piece_b
                        best_rot_a = r_a 
                        best_rot_b = r_b
                        return best_piece_a, best_rot_a, best_piece_b, best_rot_b, sol_conflicts, best_change
                    if new_conflicts - curr_conflicts < best_change:
                        if (not is_tabu) or ((self.solution[idx_piece_a], r_a, self.solution[idx_piece_b], r_b, sol_conflicts, sol_conflicts+new_conflicts-curr_conflicts) not in self.tabu and (self.solution[idx_piece_b], r_b, self.solution[idx_piece_a], r_a, sol_conflicts, sol_conflicts+new_conflicts-curr_conflicts) not in self.tabu):
                            best_change = new_conflicts - curr_conflicts
                            best_idx_piece_a = idx_piece_a
                            best_idx_piece_b = idx_piece_b
                            best_rot_a = r_a
                            best_rot_b = r_b 
                            if greedy:
                                return best_idx_piece_a, best_rot_a, best_idx_piece_b, best_rot_b, sol_conflicts, best_change
                    
                    elif altering and (new_conflicts - curr_conflicts < best_alter_change):
                        if (not is_tabu) or ((self.solution[idx_piece_a], r_a, self.solution[idx_piece_b], r_b, sol_conflicts, sol_conflicts+new_conflicts-curr_conflicts) not in self.tabu and (self.solution[idx_piece_b], r_b, self.solution[idx_piece_a], r_a, sol_conflicts, sol_conflicts+new_conflicts-curr_conflicts) not in self.tabu):
                            if len(self.tabu) == 0 or (((self.solution[idx_piece_a], (4-r_a)%4, self.solution[idx_piece_b], (4-r_b)%4, sol_conflicts+new_conflicts-curr_conflicts, sol_conflicts) != self.tabu[-1]) and ((self.solution[idx_piece_b], (4-r_b)%4, self.solution[idx_piece_a], (4-r_a)%4, sol_conflicts+new_conflicts-curr_conflicts, sol_conflicts) != self.tabu[-1])):
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