import pygame
import numpy as np
import time
import pickle
import random

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

# Zoom
zoom = 1

# Color scheme
background_color = (0, 0, 0)  # Always black
current_cell_color = (255, 255, 255)  # Initial cell color (white)
cell_colors = {}  # Dictionary to store colors of individual cells


def create_random_grid():
    global p_alive, p_dead, cell_colors
    new_grid = np.random.choice(
        [1, 0], size=(rows, cols), p=[p_alive / 100, p_dead / 100]
    )
    cell_colors = {
        (i, j): current_cell_color
        for i in range(rows)
        for j in range(cols)
        if new_grid[i, j] == 1
    }
    return new_grid


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
    "Up/Down: Change alive %",
    "Right/Left: Change speed",
    "S: Save grid",
    "L: Load grid",
    "G: Create glider",
    "+/-: Zoom in/out",
    "C: Change new cell color",
    "W: Reset all cells to white",
    "Esc: End simulation",
]

# Time to display instructions
instruction_display_time = 12  # seconds
start_time = time.time()

# Instruction box settings
box_width = 250
box_height = 300  # Adjusted height for new instruction
box_padding = 10
box_x = width - box_width - 10
box_y = 90

# Line spacing
line_spacing = small_font.get_linesize() * 1.5  # 1.5 times the regular line spacing


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
    global grid, active_cells, cell_colors
    new_grid = grid.copy()
    new_active_cells = set()
    cells_to_check = active_cells.copy()

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
                cell_colors.pop((i, j), None)
        else:
            if total == 3:
                new_grid[i, j] = 1
                new_active_cells.add((i, j))
                add_neighbors_to_set(i, j, new_active_cells)
                cell_colors[(i, j)] = (
                    current_cell_color  # Assign current color to new cell
                )

    grid = new_grid
    active_cells = new_active_cells


def update_p_values(increment):
    global p_alive, p_dead
    p_alive = max(0, min(100, p_alive + increment))
    p_dead = 100 - p_alive


def update_simulation_speed(increment):
    global simulation_speed
    simulation_speed = max(1, simulation_speed + increment)


def save_grid(filename):
    with open(filename, "wb") as f:
        pickle.dump((grid, cell_colors), f)


def load_grid(filename):
    global grid, cell_colors
    with open(filename, "rb") as f:
        grid, cell_colors = pickle.load(f)
    initialize_active_cells()


def create_glider(x, y):
    global grid, cell_colors
    glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
    grid[y : y + 3, x : x + 3] = glider
    for i in range(3):
        for j in range(3):
            if glider[i, j] == 1:
                cell_colors[(y + i, x + j)] = current_cell_color
    initialize_active_cells()


def get_statistics():
    population = np.sum(grid)
    return f"Population: {population}"


def draw_grid():
    for i, j in active_cells:
        if grid[i, j] == 1:
            x = int(j * cell_size * zoom)
            y = int(i * cell_size * zoom)
            size = int(cell_size * zoom)
            if 0 <= x < width and 0 <= y < height:
                pygame.draw.rect(
                    screen, cell_colors.get((i, j), WHITE), (x, y, size - 1, size - 1)
                )


def change_cell_color():
    global current_cell_color
    current_cell_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def reset_cells_to_white():
    global cell_colors, current_cell_color
    cell_colors = {key: WHITE for key in cell_colors}
    current_cell_color = WHITE


initialize_active_cells()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                grid = create_random_grid()
                initialize_active_cells()
            elif event.key == pygame.K_s:
                save_grid("saved_grid.pkl")
            elif event.key == pygame.K_l:
                load_grid("saved_grid.pkl")
            elif event.key == pygame.K_g:
                create_glider(cols // 2, rows // 2)
            elif event.key == pygame.K_c:
                change_cell_color()
            elif event.key == pygame.K_w:
                reset_cells_to_white()
            elif event.key == pygame.K_PLUS:
                zoom = min(zoom * 1.1, 10)
            elif event.key == pygame.K_MINUS:
                zoom = max(zoom / 1.1, 0.1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col, row = int(pos[0] / cell_size / zoom), int(pos[1] / cell_size / zoom)
            grid[row % rows, col % cols] = 1 - grid[row % rows, col % cols]
            if grid[row % rows, col % cols] == 1:
                cell_colors[(row % rows, col % cols)] = current_cell_color
            else:
                cell_colors.pop((row % rows, col % cols), None)
            active_cells.add((row % rows, col % cols))
            add_neighbors_to_set(row % rows, col % cols, active_cells)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        update_p_values(1)
    if keys[pygame.K_DOWN]:
        update_p_values(-1)
    if keys[pygame.K_RIGHT]:
        update_simulation_speed(1)
    if keys[pygame.K_LEFT]:
        update_simulation_speed(-1)

    screen.fill(background_color)

    draw_grid()

    p_text = font.render(f"Alive: {p_alive}% Dead: {p_dead}%", True, WHITE)
    speed_text = font.render(f"Speed: {simulation_speed}", True, WHITE)
    stats_text = font.render(get_statistics(), True, WHITE)
    screen.blit(p_text, (width - p_text.get_width() - 10, 10))
    screen.blit(speed_text, (width - speed_text.get_width() - 10, 50))
    screen.blit(stats_text, (10, height - 40))

    if time.time() - start_time < instruction_display_time:
        pygame.draw.rect(screen, ORANGE, (box_x, box_y, box_width, box_height))
        total_text_height = (
            len(instructions) - 1
        ) * line_spacing + small_font.get_linesize()
        text_start_y = box_y + (box_height - total_text_height) // 2
        for i, instruction in enumerate(instructions):
            instruction_text = small_font.render(instruction, True, BLACK)
            screen.blit(
                instruction_text, (box_x + box_padding, text_start_y + i * line_spacing)
            )

    update_grid()
    pygame.display.flip()
    clock.tick(simulation_speed)

pygame.quit()
