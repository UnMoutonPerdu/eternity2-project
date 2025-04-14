# import matplotlib.pyplot as plt
# import matplotlib.patches as patches

# # Dimensions de la matrice
# rows, cols = 7, 7
# total_cells = rows * cols

# fig, ax = plt.subplots(figsize=(6, 6))
# ax.set_xlim(0, cols)
# ax.set_ylim(0, rows)
# ax.set_aspect('equal')
# ax.axis('off')  # Masquer les axes

# # Génère les positions selon le parcours de bas en haut, gauche à droite
# positions = []
# for col in range(cols-1, -1, -1):
#     for row in range(rows):
#         positions.append((row, col))  # col : gauche à droite, row : bas en haut


# # Tracer chaque cellule
# for idx, (col, row) in enumerate(positions):
#     alpha = (idx + 1) / total_cells  # alpha de ~0.02 à 1
#     rect = patches.Rectangle((col, row), 1, 1, linewidth=1,
#                              edgecolor='black', facecolor=(1, 0, 0, alpha))
#     ax.add_patch(rect)
#     ax.text(col + 0.5, row + 0.5, str(idx), color='black',
#             ha='center', va='center', fontsize=8, weight='bold')

# plt.gca().invert_yaxis()  # (0,0) en bas à gauche
# plt.show()

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Dimensions
rows, cols = 7, 7
total_cells = rows * cols

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, cols)
ax.set_ylim(0, rows)
ax.set_aspect('equal')
ax.axis('off')

# Coins
corner_coords = {(0, 0), (0, rows - 1), (cols - 1, 0), (cols - 1, rows - 1)}

# Parcours de bas en haut, gauche à droite
positions = []
for col in range(cols-1, -1, -1):
    for row in range(rows):
        positions.append((row, col))  # col : gauche à droite, row : bas en haut

# Tracer chaque cellule
for idx, (col, row) in enumerate(positions):
    coord = (col, row)

    # Déterminer la couleur
    if coord in corner_coords:
        fill_color = 'blue'
    elif col == 0 or col == cols - 1 or row == 0 or row == rows - 1:
        fill_color = 'red'
    else:
        fill_color = 'yellow'

    # Dessiner la cellule
    rect = patches.Rectangle(
        (col, row), 1, 1,
        linewidth=1.5,
        edgecolor='black',
        facecolor=fill_color
    )
    ax.add_patch(rect)

    # Afficher l'indice
    ax.text(col + 0.5, row + 0.5, str(idx),
            color='black', ha='center', va='center', fontsize=8, weight='bold')

plt.gca().invert_yaxis()
plt.show()

