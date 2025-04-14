from eternity_puzzle import EternityPuzzle
import time 
import random 
import argparse
import numpy as np

from solver_heuristic import solve_heuristic
from solver_local_search import solve_local_search
from solver_advanced import solve_advanced

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', type=str, default='input')
    return parser.parse_args()

if __name__ == '__main__':
    files = ['./instances/eternity_A.txt', './instances/eternity_B.txt', './instances/eternity_C.txt', './instances/eternity_D.txt', './instances/eternity_E.txt', './instances/eternity_complet.txt']

    for f in files:
        start_time = time.time()
        sol, conflicts = solve_local_search(EternityPuzzle(f))
        print(f)
        print(f'Executed time: {time.time() - start_time}')
        print(f'Number Conflicts: {conflicts}')

    # seeds = [random.random() for _ in range(num_iter)]

    # conflicts = []
    # min_conflicts = float('inf')
    # for seed in seeds:
    #     start_time = time.time()
    #     solution_h, conflict_h = solve_local_search(eternity_puzzle, seed)
    #     h_time = time.time() - start_time
    #     if conflict_h < min_conflicts:
    #         min_conflicts = conflict_h

    #     # start_time = time.time()
    #     # solution_ls, conflict_ls = solve_local_search(eternity_puzzle, seed)
    #     # ls_time = time.time() - start_time

    #     # start_time = time.time()
    #     # solution_a, conflict_a = solve_advanced(eternity_puzzle, seed)
    #     # a_time = time.time() - start_time

    #     print(f'Seed: {seed}')
    #     print(f'Heuristic: {conflict_h} in {h_time}')
    #     conflicts.append(conflict_h)
    #     # print(f'Local Search: {conflict_ls} in {ls_time}')
    #     # print(f'Advanced: {conflict_a} in {a_time}')

    # print(f'Mean conflicts: {np.mean(conflicts)}')
    # print(f'Variance conflicts: {np.var(conflicts)}')
    # print(f'Best value: {min_conflicts}')