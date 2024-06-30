import pygame
import numpy as np
import time
import hashlib
import sys

sys.setrecursionlimit(10000)  # Increase recursion limit

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

# Initialize p values and simulation speed
p_alive, p_dead = 7, 93
simulation_speed = 10


class QuadTree:
    def __init__(self, level, alive=False):
        self.level = level
        self.alive = alive
        self.population = 1 if alive else 0
        self.nw = self.ne = self.sw = self.se = None
        self.hash = None
        self.result = None

    def compute_hash(self):
        if self.hash is None:
            if self.level == 0:
                self.hash = hashlib.md5(str(self.alive).encode()).digest()
            else:
                self.hash = hashlib.md5(
                    self.nw.compute_hash()
                    + self.ne.compute_hash()
                    + self.sw.compute_hash()
                    + self.se.compute_hash()
                ).digest()
        return self.hash


class HashLife:
    def __init__(self):
        self.cache = {}

    def create_node(self, nw, ne, sw, se):
        node = QuadTree(nw.level + 1)
        node.nw, node.ne, node.sw, node.se = nw, ne, sw, se
        node.population = nw.population + ne.population + sw.population + se.population
        hash_value = node.compute_hash()
        if hash_value in self.cache:
            return self.cache[hash_value]
        self.cache[hash_value] = node
        return node

    def next_generation(self, node):
        if node.level <= 1:
            return self.next_generation_base(node)

        if node.result is not None:
            return node.result

        n00 = self.next_generation(self.get_sub_node(node, 0, 0))
        n01 = self.next_generation(self.get_sub_node(node, 0, 1))
        n10 = self.next_generation(self.get_sub_node(node, 1, 0))
        n11 = self.next_generation(self.get_sub_node(node, 1, 1))

        result = self.create_node(n00.se, n01.sw, n10.ne, n11.nw)
        node.result = result
        return result

    def next_generation_base(self, node):
        cells = np.zeros((4, 4), dtype=bool)
        cells[0:2, 0:2] = self.get_cells(node.nw)
        cells[0:2, 2:4] = self.get_cells(node.ne)
        cells[2:4, 0:2] = self.get_cells(node.sw)
        cells[2:4, 2:4] = self.get_cells(node.se)

        new_cells = self.evolve_cells(cells)
        return self.create_node(
            self.cell_to_node(new_cells[0:2, 0:2]),
            self.cell_to_node(new_cells[0:2, 2:4]),
            self.cell_to_node(new_cells[2:4, 0:2]),
            self.cell_to_node(new_cells[2:4, 2:4]),
        )

    def get_cells(self, node):
        if node.level == 0:
            return np.array([[node.alive]], dtype=bool)
        return np.block(
            [
                [self.get_cells(node.nw), self.get_cells(node.ne)],
                [self.get_cells(node.sw), self.get_cells(node.se)],
            ]
        )

    def cell_to_node(self, cells):
        if cells.shape == (1, 1):
            return QuadTree(0, cells[0, 0])
        return self.create_node(
            self.cell_to_node(cells[0:1, 0:1]),
            self.cell_to_node(cells[0:1, 1:2]),
            self.cell_to_node(cells[1:2, 0:1]),
            self.cell_to_node(cells[1:2, 1:2]),
        )

    def evolve_cells(self, cells):
        rows, cols = cells.shape
        new_cells = np.zeros_like(cells)
        for i in range(rows):
            for j in range(cols):
                neighbors = (
                    np.sum(
                        cells[
                            max(0, i - 1) : min(i + 2, rows),
                            max(0, j - 1) : min(j + 2, cols),
                        ]
                    )
                    - cells[i, j]
                )
                if cells[i, j] == 1:
                    new_cells[i, j] = 1 if neighbors in [2, 3] else 0
                else:
                    new_cells[i, j] = 1 if neighbors == 3 else 0
        return new_cells

    def get_sub_node(self, node, x, y):
        if x == 0 and y == 0:
            return self.create_node(node.nw.se, node.ne.sw, node.sw.ne, node.se.nw)
        elif x == 0 and y == 1:
            return self.create_node(node.nw.ne, node.ne.nw, node.sw.se, node.se.sw)
        elif x == 1 and y == 0:
            return self.create_node(node.nw.sw, node.ne.se, node.sw.nw, node.se.ne)
        else:  # x == 1 and y == 1
            return self.create_node(node.nw.se, node.ne.sw, node.sw.ne, node.se.nw)


def create_random_grid():
    global p_alive, p_dead
    grid = np.random.choice([1, 0], size=(rows, cols), p=[p_alive / 100, p_dead / 100])
    # Manually set some cells to alive
    grid[rows // 2, cols // 2] = 1
    grid[rows // 2, cols // 2 + 1] = 1
    grid[rows // 2, cols // 2 - 1] = 1
    print(f"Initial population: {np.sum(grid)}")  # Debug print
    return grid


grid = create_random_grid()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

# Game loop
clock = pygame.time.Clock()
running = True

# Set to keep track of active cells and their neighbors
active_cells = set()

# Hide the cursor
pygame.mouse.set_visible(False)

# Fonts for displaying values and instructions
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Key repeat settings
pygame.key.set_repeat(200, 50)  # 200ms delay, 50ms interval

# Instructions
instructions = [
    "Space: Reinitialize grid",
    "Up: Increase alive %",
    "Down: Decrease alive %",
    "Right: Increase speed",
    "Left: Decrease speed",
    "Esc: End simulation",
]

# Time to display instructions
instruction_display_time = 12  # seconds
start_time = time.time()

# Instruction box settings
box_width = 250
box_height = 200
box_padding = 10
box_x = width - box_width - 10
box_y = 90

# Line spacing
line_spacing = small_font.get_linesize() * 1.5


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


def update_p_values(increment):
    global p_alive, p_dead
    p_alive = max(0, min(100, p_alive + increment))
    p_dead = 100 - p_alive


def update_simulation_speed(increment):
    global simulation_speed
    simulation_speed = max(1, simulation_speed + increment)


hashlife = HashLife()


def grid_to_quadtree(grid):
    level = max(grid.shape[0], grid.shape[1]).bit_length()
    size = 2**level
    padded_grid = np.pad(
        grid, ((0, size - grid.shape[0]), (0, size - grid.shape[1])), mode="constant"
    )

    def build_tree(x, y, size):
        if size == 1:
            return QuadTree(0, padded_grid[y, x])
        half = size // 2
        nw = build_tree(x, y, half)
        ne = build_tree(x + half, y, half)
        sw = build_tree(x, y + half, half)
        se = build_tree(x + half, y + half, half)
        return hashlife.create_node(nw, ne, sw, se)

    return build_tree(0, 0, size)


def quadtree_to_grid(node, rows, cols):
    full_grid = quadtree_to_full_grid(node)
    return full_grid[:rows, :cols].astype(int)


def quadtree_to_full_grid(node):
    if node.level == 0:
        return np.array([[node.alive]])
    return np.block(
        [
            [quadtree_to_full_grid(node.nw), quadtree_to_full_grid(node.ne)],
            [quadtree_to_full_grid(node.sw), quadtree_to_full_grid(node.se)],
        ]
    )


initialize_active_cells()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press ESC to exit fullscreen
                running = False
            elif event.key == pygame.K_SPACE:  # Press SPACE to reinitialize grid
                grid = create_random_grid()
                initialize_active_cells()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle cell state on mouse click
            pos = pygame.mouse.get_pos()
            col, row = pos[0] // cell_size, pos[1] // cell_size
            grid[row, col] = 1 - grid[row, col]
            active_cells.add((row, col))
            add_neighbors_to_set(row, col, active_cells)

    # Handle held down keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        update_p_values(1)
    if keys[pygame.K_DOWN]:
        update_p_values(-1)
    if keys[pygame.K_RIGHT]:
        update_simulation_speed(1)
    if keys[pygame.K_LEFT]:
        update_simulation_speed(-1)

    screen.fill(BLACK)

    try:
        # Convert grid to QuadTree, evolve, and convert back
        root = grid_to_quadtree(grid)
        evolved_root = hashlife.next_generation(root)
        new_grid = quadtree_to_grid(evolved_root, rows, cols)
        grid = new_grid

        # Ensure grid has correct dimensions
        if grid.shape != (rows, cols):
            grid = np.pad(
                grid,
                ((0, max(0, rows - grid.shape[0])), (0, max(0, cols - grid.shape[1]))),
                mode="constant",
            )
            grid = grid[:rows, :cols]

        # Update active cells
        active_cells = set(
            (i, j) for i in range(rows) for j in range(cols) if grid[i, j] == 1
        )
        new_active_cells = active_cells.copy()
        for i, j in active_cells:
            add_neighbors_to_set(i, j, new_active_cells)
        active_cells = new_active_cells

        # Debug: Print population
        print(f"Population: {np.sum(grid)}")
    except RecursionError:
        print("RecursionError occurred. Resetting the grid.")
        grid = create_random_grid()
        initialize_active_cells()
    except Exception as e:
        print(f"An error occurred: {e}")
        grid = create_random_grid()
        initialize_active_cells()

    # Draw grid
    for i in range(min(rows, grid.shape[0])):
        for j in range(min(cols, grid.shape[1])):
            if grid[i, j] == 1:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (j * cell_size, i * cell_size, cell_size - 1, cell_size - 1),
                )

    # Display p values and simulation speed
    p_text = font.render(f"Alive: {p_alive}% Dead: {p_dead}%", True, WHITE)
    speed_text = font.render(f"Speed: {simulation_speed}", True, WHITE)
    screen.blit(p_text, (width - p_text.get_width() - 10, 10))
    screen.blit(speed_text, (width - speed_text.get_width() - 10, 50))

    # Display instructions for 12 seconds
    if time.time() - start_time < instruction_display_time:
        # Draw instruction box
        pygame.draw.rect(screen, ORANGE, (box_x, box_y, box_width, box_height))

        # Calculate total height of all instructions with spacing, excluding the last extra space
        total_text_height = (
            len(instructions) - 1
        ) * line_spacing + small_font.get_linesize()

        # Calculate starting y position to center text vertically
        text_start_y = box_y + (box_height - total_text_height) // 2

        for i, instruction in enumerate(instructions):
            instruction_text = small_font.render(instruction, True, BLACK)
            screen.blit(
                instruction_text, (box_x + box_padding, text_start_y + i * line_spacing)
            )

    pygame.display.flip()
    clock.tick(simulation_speed)  # Adjust the speed of the simulation

pygame.quit()
