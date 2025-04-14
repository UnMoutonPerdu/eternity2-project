import eternity_puzzle
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
    args = parse_arguments()

    num_iter = 50
    eternity_puzzle = eternity_puzzle.EternityPuzzle(args.infile)

    seeds = [random.random() for _ in range(num_iter)]

    conflicts = []
    for seed in seeds:
        start_time = time.time()
        solution_h, conflict_h = solve_heuristic(eternity_puzzle, seed)
        h_time = time.time() - start_time

        # start_time = time.time()
        # solution_ls, conflict_ls = solve_local_search(eternity_puzzle, seed)
        # ls_time = time.time() - start_time

        # start_time = time.time()
        # solution_a, conflict_a = solve_advanced(eternity_puzzle, seed)
        # a_time = time.time() - start_time

        print(f'Seed: {seed}')
        print(f'Heuristic: {conflict_h} in {h_time}')
        conflicts.append(conflict_h)
        # print(f'Local Search: {conflict_ls} in {ls_time}')
        # print(f'Advanced: {conflict_a} in {a_time}')

    print(f'Mean conflicts: {np.mean(conflicts)}')
    print(f'Variance conflicts: {np.var(conflicts)}')