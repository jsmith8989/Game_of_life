import pygame
import numpy as np
import time

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


def create_random_grid():
    global p_alive, p_dead
    return np.random.choice([1, 0], size=(rows, cols), p=[p_alive / 100, p_dead / 100])


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
box_height = 200  # Increased height to accommodate the new line
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


def update_p_values(increment):
    global p_alive, p_dead
    p_alive = max(0, min(100, p_alive + increment))
    p_dead = 100 - p_alive


def update_simulation_speed(increment):
    global simulation_speed
    simulation_speed = max(1, simulation_speed + increment)


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

    # Draw grid
    for i, j in active_cells:
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

    update_grid()
    pygame.display.flip()
    clock.tick(simulation_speed)  # Adjust the speed of the simulation

pygame.quit()
