# Notes :
# Red = UCS, Orange = DFS, Pink = A*, Gray = Dijkstra


import pygame
import sys
import heapq
import random

pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 4

BLACK = (0, 0, 0)
WHITE = (255, 255, 255) # Pellets
YELLOW = (255, 255, 0) # Pacman
BLUE = (0, 0, 255) # Wall
GREEN = (0, 255, 0) # Fruits
RED = (255, 0, 0) # Ghost UCS
PINK = (255, 105, 180) # Ghost A*
ORANGE = (255, 165, 0) # Ghost DFS
GRAY = (128, 128, 128) # Ghost Dijkstra

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Game")

# Labyrinth
maze = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.#  #.#   #.##.#   #.#  #.#",
    "#.####.#####.##.#####.####.#",
    "#P.........................#",
    "#.####.##.########.##.####.#",
    "#......##....##....##....P.#",
    "######.##### ## #####.######",
    "     #.#            #.#     ",
    "######.# ########## #.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.#  #.#   #.##.#   #.#  #.#",
    "#.####.#####.##.#####.####.#",
    "#............P.............#",
    "############################",
]

#Labyrinth to grid
maze_grid = []
pellets = []
fruits = []
for y, row in enumerate(maze):
    maze_row = []
    for x, cell in enumerate(row):
        if cell == "#":
            maze_row.append(1) 
        else:
            maze_row.append(0)  
            if cell == ".":
                pellets.append((x, y)) 
            elif cell == "P":
                fruits.append((x, y)) 
    maze_grid.append(maze_row)

# Labyrinth render
def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "#":
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Add pellets and fruits
def draw_pellets_and_fruits():
    for pellet in pellets:
        pygame.draw.circle(screen, WHITE, (pellet[0] * CELL_SIZE + CELL_SIZE // 2, pellet[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 4)
    for fruit in fruits:
        pygame.draw.circle(screen, GREEN, (fruit[0] * CELL_SIZE + CELL_SIZE // 2, fruit[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

#Pacman movement
def move(position, direction):
    new_pos = position.copy()
    if direction == 'UP':
        new_pos[1] -= 1
    elif direction == 'DOWN':
        new_pos[1] += 1
    elif direction == 'LEFT':
        new_pos[0] -= 1
    elif direction == 'RIGHT':
        new_pos[0] += 1

    if maze_grid[new_pos[1]][new_pos[0]] == 0:
        position[0], position[1] = new_pos
        return True 
    return False  

def ghost_dfs(ghost_pos, pacman_pos):
    stack = [(tuple(ghost_pos), [])] 
    visited = set()

    while stack:
        current_pos, path = stack.pop()

        if current_pos in visited:
            continue

        visited.add(current_pos)

        if current_pos == tuple(pacman_pos):
            if path:
                next_pos = path[0]
                ghost_pos[0], ghost_pos[1] = next_pos
            return

        x, y = current_pos
        neighbors = [
            (x - 1, y),  
            (x + 1, y),  
            (x, y - 1),  
            (x, y + 1),  
        ]

        neighbors.sort(key=lambda n: abs(n[0] - pacman_pos[0]) + abs(n[1] - pacman_pos[1]))

        for nx, ny in neighbors:
            if 0 <= ny < len(maze_grid) and 0 <= nx < len(maze_grid[0]) and maze_grid[ny][nx] == 0:
                stack.append(((nx, ny), path + [(nx, ny)]))

def get_neighbors(pos):
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
    for dx, dy in directions:
        nx, ny = pos[0] + dx, pos[1] + dy
        if 0 <= nx < len(maze_grid[0]) and 0 <= ny < len(maze_grid):
            if maze_grid[ny][nx] == 0: 
                neighbors.append((nx, ny))
    return neighbors

def ghost_ucs(ghost1_pos, pacman_pos):
    def get_neighbors(pos):
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= ny < len(maze_grid) and 0 <= nx < len(maze_grid[0]):
                if maze_grid[ny][nx] == 0:  
                    neighbors.append((nx, ny))
        return neighbors

    priority_queue = []
    heapq.heappush(priority_queue, (0, tuple(ghost1_pos), []))
    visited = set()

    while priority_queue:
        cost, current_pos, path = heapq.heappop(priority_queue)

        if current_pos in visited:
            continue
        visited.add(current_pos)

        if current_pos == tuple(pacman_pos):
            if path:
                ghost1_pos[0], ghost1_pos[1] = path[0]  
            return

        for neighbor in get_neighbors(current_pos):
            if neighbor not in visited:
                new_cost = cost + 1 
                heapq.heappush(priority_queue, (new_cost, neighbor, path + [neighbor]))

    return

# Disktra
def ghost_dijkstra(ghost_pos, pacman_pos):
    def get_neighbors(pos):
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= ny < len(maze_grid) and 0 <= nx < len(maze_grid[0]):
                if maze_grid[ny][nx] == 0:  
                    neighbors.append((nx, ny))
        return neighbors

    priority_queue = []
    heapq.heappush(priority_queue, (0, tuple(ghost_pos), []))
    visited = set()
    distances = {tuple(ghost_pos): 0}

    while priority_queue:
        cost, current_pos, path = heapq.heappop(priority_queue)

        if current_pos in visited:
            continue
        visited.add(current_pos)

        if current_pos == tuple(pacman_pos):
            if path:
                ghost_pos[0], ghost_pos[1] = path[0]  
            return

        for neighbor in get_neighbors(current_pos):
            if neighbor not in visited:
                new_cost = cost + 1 
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    heapq.heappush(priority_queue, (new_cost, neighbor, path + [neighbor]))

    return

# A*
def ghost_a_star(ghost_pos, pacman_pos):
    def heuristic(pos):
        return abs(pos[0] - pacman_pos[0]) + abs(pos[1] - pacman_pos[1])

    priority_queue = []
    heapq.heappush(priority_queue, (0, tuple(ghost_pos), []))
    visited = set()

    while priority_queue:
        cost, current_pos, path = heapq.heappop(priority_queue)

        if current_pos in visited:
            continue
        visited.add(current_pos)

        if current_pos == tuple(pacman_pos):
            if path:
                ghost_pos[0], ghost_pos[1] = path[0]  
            return

        for neighbor in get_neighbors(current_pos):
            if neighbor not in visited:
                new_cost = cost + 1 
                heapq.heappush(priority_queue, (new_cost + heuristic(neighbor), neighbor, path + [neighbor]))

    return

# Initialize pacman and ghost position
pacman_pos = [14, 9] 
ghost1_pos = [1, 1] # red
ghost2_pos = [1, 15] # orange
ghost3_pos = [26, 1] # pink
ghost4_pos = [26, 15] # gray

pacman_direction = None
last_valid_direction = None

score = 0

def reset_game():
    global pacman_pos, ghost1_pos, ghost2_pos, ghost3_pos, ghost4_pos, pacman_direction, last_valid_direction, game_over, pellets, fruits, score
    pacman_pos = [14, 9]  # Pacman starting position
    ghost1_pos = [1, 1]  # Red
    ghost2_pos = [1, 15]  # Orange
    ghost3_pos = [26, 1]  # Pink
    ghost4_pos = [26, 15]  # Gray
    score = 0
    pacman_direction = None
    last_valid_direction = None
    game_over = False
    pellets = [(x, y) for y, row in enumerate(maze) for x, cell in enumerate(row) if cell == "."]
    fruits = [(x, y) for y, row in enumerate(maze) for x, cell in enumerate(row) if cell == "P"]


# Game loop
clock = pygame.time.Clock()
running = True
game_over = False
game_won = False
LOGIC_INTERVAL = 100
last_update_time = pygame.time.get_ticks()

while running:
    screen.fill(BLACK)

    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if (game_over or game_won) and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game()
                game_won = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                pacman_direction = 'UP'
            elif event.key == pygame.K_s:
                pacman_direction = 'DOWN'
            elif event.key == pygame.K_a:
                pacman_direction = 'LEFT'
            elif event.key == pygame.K_d:
                pacman_direction = 'RIGHT'

    # Update game logic at fixed intervals
    if not game_over and not game_won and current_time - last_update_time >= LOGIC_INTERVAL:
        if pacman_direction:
            moved = move(pacman_pos, pacman_direction)
            if moved:
                last_valid_direction = pacman_direction
            elif last_valid_direction:
                move(pacman_pos, last_valid_direction)

        # Check collisions and update score
        if tuple(pacman_pos) in pellets:
            pellets.remove(tuple(pacman_pos))
            score += 10
        if tuple(pacman_pos) in fruits:
            fruits.remove(tuple(pacman_pos))
            score += 50

        # Check for victory condition
        if not pellets:
            game_won = True

        # Update ghost positions
        ghost_ucs(ghost1_pos, pacman_pos)
        ghost_dfs(ghost2_pos, pacman_pos)
        ghost_a_star(ghost3_pos, pacman_pos)
        ghost_dijkstra(ghost4_pos, pacman_pos)

        # Check for collisions with ghosts
        if pacman_pos in [ghost1_pos, ghost2_pos, ghost3_pos, ghost4_pos]:
            game_over = True

        last_update_time = current_time

    # Render everything
    draw_maze()
    draw_pellets_and_fruits()

    # Draw Pacman and ghosts
    pygame.draw.circle(screen, YELLOW, (pacman_pos[0] * CELL_SIZE + CELL_SIZE // 2, pacman_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    pygame.draw.circle(screen, RED, (ghost1_pos[0] * CELL_SIZE + CELL_SIZE // 2, ghost1_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    pygame.draw.circle(screen, ORANGE, (ghost2_pos[0] * CELL_SIZE + CELL_SIZE // 2, ghost2_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    pygame.draw.circle(screen, PINK, (ghost3_pos[0] * CELL_SIZE + CELL_SIZE // 2, ghost3_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    pygame.draw.circle(screen, GRAY, (ghost4_pos[0] * CELL_SIZE + CELL_SIZE // 2, ghost4_pos[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 350))

    # Handle "Game Over" and "You Won" screens
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        print_score = font.render(f"Score: {score}", True, WHITE)
        print_score_rect = print_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_text_rect)
        screen.blit(print_score, print_score_rect)

    elif game_won:
        font = pygame.font.Font(None, 74)
        text = font.render("YOU WON!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        print_score = font.render(f"Score: {score}", True, WHITE)
        print_score_rect = print_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_text_rect)
        screen.blit(print_score, print_score_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()