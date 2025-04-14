# ######### HEURISTIC ###########
# # Placement des pieces en suivant la spirale + orientation minimisant les conflits
#     index_visited_corner = []
#     index_visited_border = []
#     index_visited_inner = [] 
#     random.shuffle(corner_pieces)
#     random.shuffle(border_pieces)
#     random.shuffle(inner_pieces)
#     for k in all_index:
#         if k in corner_index:
#             index_best = None
#             best_orientation = None 
#             min_conflict = 4
#             for i in range(len(corner_pieces)):
#                 if i not in index_visited_corner:
#                     rotations = [0, 1, 2, 3]
#                     random.shuffle(rotations)
#                     for r in rotations:
#                         if index_best == None:
#                             index_best = i 
#                             best_orientation = r
#                         solution[k] = eternity_puzzle.generate_rotation(corner_pieces[i])[r]
#                         if count_conflict(eternity_puzzle, solution, k) < min_conflict:
#                             min_conflict = count_conflict(eternity_puzzle, solution, k)
#                             index_best = i 
#                             best_orientation = r    
#             solution[k] = eternity_puzzle.generate_rotation(corner_pieces[index_best])[best_orientation]
#             index_visited_corner.append(index_best)
#         elif k in border_index:
#             index_best = None
#             best_orientation = None
#             min_conflict = 4
#             for i in range(len(border_pieces)):
#                 if i not in index_visited_border:
#                     rotations = [0, 1, 2, 3]
#                     random.shuffle(rotations)
#                     for r in rotations:
#                         if index_best == None:
#                             index_best = i 
#                             best_orientation = r
#                         solution[k] = eternity_puzzle.generate_rotation(border_pieces[i])[r]
#                         if count_conflict(eternity_puzzle, solution, k) < min_conflict:
#                             min_conflict = count_conflict(eternity_puzzle, solution, k)
#                             index_best = i 
#                             best_orientation = r
#             solution[k] = eternity_puzzle.generate_rotation(border_pieces[index_best])[best_orientation]
#             index_visited_border.append(index_best)
#         elif k in inner_index:
#             index_best = None
#             best_orientation = None
#             min_conflict = 4
#             for i in range(len(inner_pieces)):
#                 if i not in index_visited_inner:
#                     rotations = [0, 1, 2, 3]
#                     random.shuffle(rotations)
#                     for r in range(4):
#                         if index_best == None:
#                             index_best = i 
#                             best_orientation = r
#                         solution[k] = eternity_puzzle.generate_rotation(inner_pieces[i])[r]
#                         if count_conflict(eternity_puzzle, solution, k) < min_conflict:
#                             min_conflict = count_conflict(eternity_puzzle, solution, k)
#                             index_best = i 
#                             best_orientation = r
#             solution[k] = eternity_puzzle.generate_rotation(inner_pieces[index_best])[best_orientation]
#             index_visited_inner.append(index_best)

#     piece2conflict, conflict2piece = generate_conflicts(eternity_puzzle, solution)
    
#     return solution, eternity_puzzle.get_total_n_conflict(solution), piece2conflict, conflict2piece



############# LOCAL SEARCH ###################

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