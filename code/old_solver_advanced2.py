import copy 
import random 
import time 
from eternity_puzzle import EternityPuzzle
from typing import List, Tuple
from math import exp, comb
# from solver_heuristic import get_spiral
from code.old_solver_advanced import swap_2, rotate_inner
#####################
# Constantes Utiles #
#####################
GRAY = 0
BLACK = 23
RED = 24
WHITE = 25

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3
#########################
# Configuration Globale #
#########################
MAX_TABU_SIZE = 300
BETA_1 = 0.5
BETA_2 = 6000
###################
# Classe Solution #
###################
class Solution:
    def __init__(self, eternity_puzzle: EternityPuzzle, sol, tabu_list=[], max_tabu_size=MAX_TABU_SIZE):
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
        self.homogenous_pieces = comb(4, 2) + comb(4*(eternity_puzzle.board_size-2), 2) + comb((eternity_puzzle.board_size-2)**2, 2)
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
        # for k in self.all_index:
        #     piece2conflict[k] = count_conflict(self, k)
        #     conflict2piece[count_conflict(self, k)].append(k)
        return piece2conflict, conflict2piece

# Commpte le nombre de conflits pour une piece a la position k dans le puzzle
def count_conflict(solution: Solution, k: int) -> int:
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

#####################
# Solution Initiale #
#####################

# Construit une solution initiale selon l'heuristique de solver_heuristic.py
def build_greedy(eternity_puzzle):
    solution = [0]*eternity_puzzle.n_piece
    sol = Solution(eternity_puzzle, solution)

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

    return Solution(eternity_puzzle, solution)

############################
# Fonctions de Destruction #
############################

# Detruit de facon aleatoire une certaine portion du puzzle
def destruct_random(solution: Solution, ratio_destruction: float):
    nb_destructed_pieces = int(solution.get_puzzle().board_size**2 * ratio_destruction)
    id_destructed_pieces = random.sample(range(solution.get_puzzle().board_size**2), nb_destructed_pieces)
    new_sol = Solution(solution.get_puzzle(), copy.deepcopy(solution.get_sol()))
    destructed_pieces = [] 
    for i in id_destructed_pieces:
        new_sol.get_sol()[i] = 0
        destructed_pieces.append(solution.get_sol()[i])

    return new_sol, id_destructed_pieces, destructed_pieces

# Detruit toutes les pieces en conflit
def destruct_all_conflicts(solution: Solution):
    new_sol = Solution(solution.get_puzzle(), copy.deepcopy(solution.get_sol()))
    destructed_pieces = [] 
    id_destructed_pieces = [] 
    for i, piece in enumerate(solution.get_sol()):
        if count_conflict(solution, i) > 0:
            id_destructed_pieces.append(i)
            destructed_pieces.append(piece)
            new_sol[i] = 0 
    
    return new_sol, id_destructed_pieces, destructed_pieces

# Detruit au maximum la portion de pieces demandees
def destruct_ratio_conflicts(solution: Solution, ratio_destruction: float):
    # Recupere les pieces et leurs conflits. Melange et tri par conflits  
    pieces_with_conflicts = [(i, count_conflict(solution, i)) for i in range(solution.get_puzzle().n_piece)]
    random.shuffle(pieces_with_conflicts)
    pieces_with_conflicts.sort(key=lambda x: -x[1])
    pieces_with_conflicts = [i for (i, _) in pieces_with_conflicts]

    # On ne fait que le minimum de destruction requises par le ratio 
    nb_destructed_pieces = min(int(solution.get_puzzle().board_size**2 * ratio_destruction), len(pieces_with_conflicts))
    new_sol = Solution(solution.get_puzzle(), copy.deepcopy(solution.get_sol()))
    destructed_pieces = [] 
    id_destructed_pieces = [i for i in pieces_with_conflicts[:nb_destructed_pieces]]
    for i in id_destructed_pieces:
        destructed_pieces.append(solution.get_sol()[i])
        new_sol.get_sol()[i] = 0
    
    return new_sol, id_destructed_pieces, destructed_pieces

def destruct_all_conflicts_and_ratio(solution: Solution, ratio_destruction: float):
    # Recupere les pieces et leurs conflits. Melange et tri par conflits  
    pieces_with_conflicts = [(i, count_conflict(solution, i)) for i in range(solution.get_puzzle().n_piece)]
    pieces_without_conflicts = [k[0] for k in pieces_with_conflicts if k[1] == 0]
    random.shuffle(pieces_with_conflicts)
    pieces_with_conflicts.sort(key=lambda x: -x[1])
    pieces_with_conflicts = [i for (i, j) in pieces_with_conflicts if j > 0]

    new_sol = Solution(solution.get_puzzle(), copy.deepcopy(solution.get_sol()))
    destructed_pieces = [] 
    id_destructed_pieces = [i for i in pieces_with_conflicts]
    random.shuffle(pieces_without_conflicts)
    id_destructed_pieces = id_destructed_pieces + [i for i in pieces_without_conflicts[:int(solution.get_puzzle().board_size**2 * ratio_destruction/2)]]
    for i in id_destructed_pieces:
        destructed_pieces.append(solution.get_sol()[i])
        new_sol.get_sol()[i] = 0

    return new_sol, id_destructed_pieces, destructed_pieces

###########################
# Fonctions de Réparation #
###########################

# Replace les pieces detruites de manieres aleatoires avec une rotation aleatoire dans les emplacements vides
def repair_random(destructed_sol: Solution, id_destructed_pieces: List[int], destructed_pieces: List[Tuple[int]]):
    new_sol = Solution(destructed_sol.get_puzzle(), copy.deepcopy(destructed_sol.get_sol()))
    random.shuffle(destructed_pieces)
    random.shuffle(id_destructed_pieces)

    for i in id_destructed_pieces:
        new_sol.get_sol()[i] = random.choice(new_sol.get_puzzle().generate_rotation(destructed_pieces[i]))

    new_sol.generate_conflicts()
    return new_sol

# Replace les pieces dans chaque emplacement vide en prenant a chaque fois celle qui minimise le plus les conflits
def repair_based_heuristic(destructed_sol: Solution, id_destructed_pieces: List[int], destructed_pieces: List[Tuple[int]]):
    new_sol = Solution(destructed_sol.get_puzzle(), copy.deepcopy(destructed_sol.get_sol()))
    random.shuffle(destructed_pieces)
    random.shuffle(id_destructed_pieces)
    pieces_replaced = []
    for i in id_destructed_pieces:
        best_piece = None 
        best_rot = None 
        min_conflicts = 42
        for i_piece, piece in enumerate(destructed_pieces):
            if i_piece not in pieces_replaced:
                for rot, piece_rot in enumerate(new_sol.get_puzzle().generate_rotation(piece)):
                    new_sol.get_sol()[i] = piece_rot
                    conflicts = count_conflict(new_sol, i)
                    if conflicts < min_conflicts:
                        best_piece = i_piece
                        best_rot = rot 
                        min_conflicts = conflicts
                    if min_conflicts == 0: 
                        break 
        
        new_sol.get_sol()[i] = new_sol.get_puzzle().generate_rotation(destructed_pieces[best_piece])[best_rot]
        pieces_replaced.append(best_piece)

    return new_sol

###########################
# Fonctions d'Acceptation #
###########################

# Accepte une solution seulement si elle est meilleure que la precedente
def accept_better(old_score: int, new_score: int):
    return new_score < old_score

# Permet de diversifier un peu plus que la fonction precedente 
def accept_equal_or_better(old_score: int, new_score: int):
    return new_score <= old_score

# Accepte toutes les solutions, qu'elle soit meilleure ou moins bonne que la precedente
def accept_every_solution(old_score: int, new_score: int):
    return True 

##########
# Solver #
##########
def solve_advanced(eternity_puzzle: EternityPuzzle):
    """
    Your solver for the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    ######### CONFIGURATION ##########
    MAX_TIME = 3600
    RATIO_DESTRUCTION = 0.1
    NB_BEST_RESTART_BEF_RANDOM = 1
    NB_RANDOM_RESTART_BEF_BEST = 2 
    DESTRUCT_FCT = destruct_ratio_conflicts
    REPAIR_FCT   = repair_based_heuristic
    ACCEPT_FCT   = accept_every_solution
    MAX_ITER = 12000
    MAX_ITER_TABU = 400
    ITER_CHANGE_RATIO = 10
    LOG = True 
    SEED = False
    SEED_VALUE = 0.23293498870400287
    ##################################
    if SEED:
        random.seed(SEED_VALUE)
        print(f'Seed: {SEED_VALUE}')
    best_sol_overall = build_greedy(eternity_puzzle)
    best_score_overall = eternity_puzzle.get_total_n_conflict(best_sol_overall.get_sol())

    if LOG:
        print(f'Initial Solution - Score: {best_score_overall}')

    nb_iter = 1
    start_time = time.time() 
    iter_to_change_ratio = 0
    while best_score_overall != 0 and (time.time() - start_time) <= MAX_TIME:
        if iter_to_change_ratio < ITER_CHANGE_RATIO:
            NB_BEST_RESTART_BEF_RANDOM = 1
            NB_RANDOM_RESTART_BEF_BEST = 2 
        else:
            NB_BEST_RESTART_BEF_RANDOM = 2
            NB_RANDOM_RESTART_BEF_BEST = 1 

        if (nb_iter % (NB_BEST_RESTART_BEF_RANDOM + NB_RANDOM_RESTART_BEF_BEST)) < NB_BEST_RESTART_BEF_RANDOM:
            curr_sol = Solution(eternity_puzzle, best_sol_overall.get_sol())
            curr_score = best_score_overall
            DESTRUCT_FCT = destruct_ratio_conflicts
            if LOG:
                print(f'Start of LNS - Best - Score initial: {curr_score} - Iteration: {nb_iter}')
        else:
            curr_sol = build_greedy(eternity_puzzle)
            curr_score = eternity_puzzle.get_total_n_conflict(curr_sol.get_sol())
            DESTRUCT_FCT = destruct_ratio_conflicts
            if LOG:
                print(f'Start of LNS - Random - Score initial: {curr_score} - Iteration: {nb_iter}')
        # nb_iter += 1 

        # LNS # 
        iter_without_improvement = 0
        iter_without_accept      = 0
        start_time_LNS = time.time()
        best_sol = Solution(eternity_puzzle, curr_sol.get_sol())
        best_score = curr_score
        tabu_done = True 
        while (not tabu_done) or (best_score != 0 and (time.time() - start_time) <= MAX_TIME and iter_without_accept < MAX_ITER and iter_without_improvement < MAX_ITER) :
            destructed_sol, id_destructed_pieces, destructed_pieces = DESTRUCT_FCT(curr_sol, ratio_destruction=RATIO_DESTRUCTION)
            repaired_sol = REPAIR_FCT(destructed_sol, id_destructed_pieces, destructed_pieces)
            new_score = eternity_puzzle.get_total_n_conflict(repaired_sol.get_sol())

            if new_score == 0:
                best_sol = Solution(eternity_puzzle, repaired_sol.get_sol())
                best_score = new_score
                break 
            else:
                if ACCEPT_FCT(curr_score, new_score):
                    iter_without_accept = 0
                    curr_sol = Solution(eternity_puzzle, repaired_sol.get_sol())
                    curr_score = new_score

                    if curr_score <= best_score:
                        if curr_score < best_score:
                            iter_without_improvement = 0 
                        else:
                            iter_without_improvement += 1
                        best_sol = Solution(eternity_puzzle, curr_sol.get_sol())
                        best_score = curr_score
                    else:
                        iter_without_improvement += 1
                else:
                    iter_without_accept += 1

            if not tabu_done and (iter_without_accept == MAX_ITER or iter_without_improvement == MAX_ITER):
                start_time_tabu = time.time()
                if LOG:
                    print(f'Start Tabu Search - Score Initial: {best_score}')
                tabu_done = True 
                iter_without_accept = 0
                iter_without_improvement = 0
                curr_sol = Solution(eternity_puzzle, copy.deepcopy(best_sol.get_sol()))
                iter_tabu = 0
                while iter_tabu < MAX_ITER_TABU and (time.time() - start_time) <= MAX_TIME:
                    iter_tabu += 1
                    rot_BP, rot_BR, rot_base_conflicts, rot_change = rotate_inner(curr_sol, greedy=False, is_tabu=True, type_piece=0)
                    swap_BP_a, swap_BR_a, swap_BP_b, swap_BR_b, swap_base_conflicts, swap_change = swap_2(curr_sol, greedy=False, is_tabu=True, type_piece=2, random_swap=False, altering=True)
                    if rot_change != 0 and rot_change < swap_change:
                        curr_sol.add_tabu((curr_sol.get_sol()[rot_BP], rot_BR, rot_base_conflicts))
                        curr_sol.get_sol()[rot_BP] = eternity_puzzle.generate_rotation(curr_sol.get_sol()[rot_BP])[rot_BR]
                        curr_sol.generate_conflicts()
                    else:
                        curr_sol.add_tabu((curr_sol.get_sol()[swap_BP_a], swap_BR_a, curr_sol.get_sol()[swap_BP_b], swap_BR_b, swap_base_conflicts, swap_base_conflicts+swap_change))
                        temp = curr_sol.get_sol()[swap_BP_a]
                        curr_sol.get_sol()[swap_BP_a] = eternity_puzzle.generate_rotation(curr_sol.get_sol()[swap_BP_b])[swap_BR_a]
                        curr_sol.get_sol()[swap_BP_b] = eternity_puzzle.generate_rotation(temp)[swap_BR_b]
                        curr_sol.generate_conflicts()
                    curr_sol.clear_tabu()
                    new_conflicts = eternity_puzzle.get_total_n_conflict(curr_sol.get_sol())

                    if new_conflicts == 0:
                        best_sol = Solution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()))
                        best_score = new_conflicts
                        break 
                    if new_conflicts < eternity_puzzle.get_total_n_conflict(best_sol.get_sol()):
                        if LOG:
                            print(f'New Best Score in Tabu Search - New Score: {new_conflicts}')
                        best_sol = Solution(eternity_puzzle, copy.deepcopy(curr_sol.get_sol()))
                        best_score = new_conflicts
                        if best_score < best_score_overall:
                            if LOG:
                                print(f'New Best Score Overall in Tabu Search - New Score: {new_conflicts}')
                            # iter_to_change_ratio = 0
                            best_sol_overall = Solution(eternity_puzzle, best_sol.get_sol())
                            best_score_overall = best_score
                curr_sol.clear_tabu()
                if LOG:
                    print(f'End Tabu Search - Score Final: {eternity_puzzle.get_total_n_conflict(curr_sol.get_sol())} - Temps d\'execution: {time.time() - start_time_tabu}')

        if LOG:
            print(f'End of LNS - Score final: {best_score} - Iteration: {nb_iter} - Temps d\'execution: {time.time() - start_time_LNS}')
        
        if best_score == 0:
            best_sol_overall = Solution(eternity_puzzle, best_sol.get_sol())
            best_score_overall = 0
            break 
        elif best_score <= best_score_overall:
            if best_score == best_score_overall:
                iter_to_change_ratio += 1
            else:
                iter_to_change_ratio = 0
            best_sol_overall = Solution(eternity_puzzle, best_sol.get_sol())
            best_score_overall = best_score
            if LOG:
                print(f'New best solution - New score: {best_score_overall} - Iteration: {nb_iter} - Temps d\'execution: {time.time() - start_time}')
        else:
            iter_to_change_ratio += 1
            if LOG:
                print(f'No improvement - Current score: {best_score_overall} - Iteration: {nb_iter} - Temps d\'execution: {time.time() - start_time}')
        nb_iter += 1

    return best_sol_overall.get_sol(), best_score_overall