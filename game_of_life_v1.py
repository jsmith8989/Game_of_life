import pygame
import numpy as np

pygame.init()

# Get the screen resolution
infoObject = pygame.display.Info()
width, height = infoObject.current_w, infoObject.current_h

# Set up the display (fullscreen)
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Conway's Game of Life")

# Set up the grid
cell_size = 3
cols, rows = width // cell_size, height // cell_size
grid = np.random.choice([0, 1], size=(rows, cols), p=[0.85, 0.15])

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game loop
clock = pygame.time.Clock()
running = True

# Set to keep track of active cells and their neighbors
active_cells = set()


def add_neighbors_to_set(i, j, cell_set):
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            ni, nj = (i + di) % rows, (j + dj) % cols
            cell_set.add((ni, nj))


def initialize_active_cells():
    global active_cells
    active_cells = set(
        (i, j) for i in range(rows) for j in range(cols) if grid[i, j] == 1
    )
    new_active_cells = active_cells.copy()
    for i, j in active_cells:
        add_neighbors_to_set(i, j, new_active_cells)
    active_cells = new_active_cells


def update_grid():
    global grid, active_cells
    new_grid = grid.copy()
    new_active_cells = set()
    cells_to_check = active_cells.copy()  # Create a copy to iterate over

    for i, j in cells_to_check:
        total = int(
            (
                grid[i, (j - 1) % cols]
                + grid[i, (j + 1) % cols]
                + grid[(i - 1) % rows, j]
                + grid[(i + 1) % rows, j]
                + grid[(i - 1) % rows, (j - 1) % cols]
                + grid[(i - 1) % rows, (j + 1) % cols]
                + grid[(i + 1) % rows, (j - 1) % cols]
                + grid[(i + 1) % rows, (j + 1) % cols]
            )
        )

        if grid[i, j] == 1:
            if 2 <= total <= 3:
                new_grid[i, j] = 1
                new_active_cells.add((i, j))
                add_neighbors_to_set(i, j, new_active_cells)
            else:
                new_grid[i, j] = 0
        else:
            if total == 3:
                new_grid[i, j] = 1
                new_active_cells.add((i, j))
                add_neighbors_to_set(i, j, new_active_cells)

    grid = new_grid
    active_cells = new_active_cells


initialize_active_cells()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press ESC to exit fullscreen
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle cell state on mouse click
            pos = pygame.mouse.get_pos()
            col, row = pos[0] // cell_size, pos[1] // cell_size
            grid[row, col] = 1 - grid[row, col]
            active_cells.add((row, col))
            add_neighbors_to_set(row, col, active_cells)

    screen.fill(BLACK)

    # Draw grid
    for i, j in active_cells:
        if grid[i, j] == 1:
            pygame.draw.rect(
                screen,
                WHITE,
                (j * cell_size, i * cell_size, cell_size - 1, cell_size - 1),
            )

    update_grid()
    pygame.display.flip()
    clock.tick(10)  # Adjust the speed of the simulation

pygame.quit()
