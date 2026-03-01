import pygame
import math
import random
import time
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# Setup Display Dimensions
WIDTH, HEIGHT = 1000, 700
GRID_WIDTH = 700
UI_WIDTH = WIDTH - GRID_WIDTH
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Pathfinding Agent")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)      # Frontier
RED = (255, 0, 0)           # Visited
GREEN = (0, 255, 0)         # Path
BLUE = (0, 0, 255)          # Agent / Start
ORANGE = (255, 165, 0)      # Goal
PURPLE = (128, 0, 128)      # UI Accent

# Fonts
FONT = pygame.font.SysFont("Arial", 18)
FONT_BOLD = pygame.font.SysFont("Arial", 18, bold=True)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == YELLOW
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == BLUE
    def is_end(self): return self.color == ORANGE
    def reset(self): self.color = WHITE
    def make_start(self): self.color = BLUE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = YELLOW
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = ORANGE
    def make_path(self): self.color = GREEN
    def draw(self, win): pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

# --- Heuristics ---
def h_manhattan(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def h_euclidean(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# --- Path Reconstruction ---
def reconstruct_path(came_from, current, draw):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
        current.make_path()
        draw()
    return path[::-1] # Return reversed path (start to end)

# --- Pathfinding Algorithm ---
def find_path(draw, grid, start, end, algo="A*", heuristic="Manhattan"):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    h_func = h_manhattan if heuristic == "Manhattan" else h_euclidean
    
    nodes_expanded = 0
    start_time = time.time()

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash = {item[2] for item in open_set.queue}

        if current == end:
            end.make_end()
            start.make_start()
            path = reconstruct_path(came_from, end, draw)
            exec_time = (time.time() - start_time) * 1000 # ms
            return path, nodes_expanded, exec_time

        if current != start:
            current.make_closed()
            nodes_expanded += 1

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                h = h_func(neighbor.get_pos(), end.get_pos())
                
                # Formula differentiation
                if algo == "A*":
                    f_score = temp_g_score + h
                else: # GBFS
                    f_score = h

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        neighbor.make_open()
        draw()
    return None, nodes_expanded, (time.time() - start_time) * 1000

# --- Grid Helpers ---
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRAY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRAY, (j * gap, 0), (j * gap, width))

def generate_random_maze(grid, start, end, density=0.3):
    for row in grid:
        for node in row:
            if node != start and node != end:
                node.reset()
                if random.random() < density:
                    node.make_barrier()

def draw_ui(win, metrics, config):
    pygame.draw.rect(win, DARK_GRAY, (GRID_WIDTH, 0, UI_WIDTH, HEIGHT))
    
    texts = [
        "DYNAMIC PATHFINDING",
        "-"*25,
        f"Algorithm: {config['algo']}",
        f"Heuristic: {config['heuristic']}",
        f"Dynamic Mode: {'ON' if config['dynamic'] else 'OFF'}",
        "-"*25,
        "METRICS:",
        f"Nodes Visited: {metrics['nodes']}",
        f"Path Cost: {metrics['cost']}",
        f"Time (ms): {metrics['time']:.2f}",
        "-"*25,
        "CONTROLS:",
        "Left Click: Draw Wall",
        "Right Click: Erase Wall",
        "[C] Clear Grid",
        "[M] Generate Maze (30%)",
        "[A] Toggle A* / GBFS",
        "[H] Toggle Heuristic",
        "[D] Toggle Dynamic Mode",
        "[SPACE] Start Search"
    ]

    y_offset = 20
    for text in texts:
        color = PURPLE if "DYNAMIC" in text else WHITE
        font = FONT_BOLD if "METRICS" in text or "CONTROLS" in text else FONT
        rendered = font.render(text, True, color)
        win.blit(rendered, (GRID_WIDTH + 15, y_offset))
        y_offset += 30

def draw_main(win, grid, rows, width, metrics, config):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    draw_ui(win, metrics, config)
    pygame.display.update()

# --- Main Loop ---
def main():
    ROWS = 35
    grid = make_grid(ROWS, GRID_WIDTH)

    start = grid[2][2]
    end = grid[ROWS-3][ROWS-3]
    start.make_start()
    end.make_end()

    run = True
    metrics = {"nodes": 0, "cost": 0, "time": 0.0}
    config = {"algo": "A*", "heuristic": "Manhattan", "dynamic": False}
    
    agent_path = []
    agent_pos_index = 0
    is_agent_moving = False

    while run:
        draw_main(WIN, grid, ROWS, GRID_WIDTH, metrics, config)
        
        # --- Dynamic Agent Movement Logic ---
        if is_agent_moving and agent_path:
            pygame.time.delay(100) # Speed of agent
            
            # 1. Dynamic Obstacle Spawning
            if config['dynamic'] and random.random() < 0.05: # 5% chance per step
                rx, ry = random.randint(0, ROWS-1), random.randint(0, ROWS-1)
                r_node = grid[rx][ry]
                if not r_node.is_start() and not r_node.is_end() and not r_node.is_barrier():
                    r_node.make_barrier()
                    # 2. Re-planning Mechanism
                    # Check if spawned obstacle is on our remaining path
                    if r_node in agent_path[agent_pos_index:]:
                        print("Obstacle spawned on path! Replanning...")
                        for row in grid:
                            for node in row:
                                if not node.is_barrier() and not node.is_end() and node != agent_path[agent_pos_index]:
                                    node.reset()
                        
                        start = agent_path[agent_pos_index]
                        start.make_start()
                        
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                                
                        new_path, nodes, exec_time = find_path(lambda: draw_main(WIN, grid, ROWS, GRID_WIDTH, metrics, config), grid, start, end, config['algo'], config['heuristic'])
                        
                        if new_path:
                            agent_path = new_path
                            agent_pos_index = 0
                            metrics['nodes'] += nodes
                            metrics['cost'] = len(agent_path)
                            metrics['time'] += exec_time
                        else:
                            print("No path found during replanning!")
                            is_agent_moving = False

            # Move Agent
            if is_agent_moving and agent_pos_index < len(agent_path):
                # Clean up old agent visual
                if agent_pos_index > 0:
                    agent_path[agent_pos_index-1].make_path()
                
                current_agent_node = agent_path[agent_pos_index]
                if current_agent_node != end:
                    current_agent_node.color = BLUE # Agent color
                agent_pos_index += 1
            else:
                is_agent_moving = False # Reached end

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if not is_agent_moving:
                if pygame.mouse.get_pressed()[0]: # Left Click
                    pos = pygame.mouse.get_pos()
                    if pos[0] < GRID_WIDTH:
                        row, col = pos[0] // (GRID_WIDTH // ROWS), pos[1] // (GRID_WIDTH // ROWS)
                        node = grid[row][col]
                        if node != start and node != end:
                            node.make_barrier()

                elif pygame.mouse.get_pressed()[2]: # Right Click
                    pos = pygame.mouse.get_pos()
                    if pos[0] < GRID_WIDTH:
                        row, col = pos[0] // (GRID_WIDTH // ROWS), pos[1] // (GRID_WIDTH // ROWS)
                        node = grid[row][col]
                        node.reset()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        config['algo'] = "GBFS" if config['algo'] == "A*" else "A*"
                    if event.key == pygame.K_h:
                        config['heuristic'] = "Euclidean" if config['heuristic'] == "Manhattan" else "Manhattan"
                    if event.key == pygame.K_d:
                        config['dynamic'] = not config['dynamic']
                    if event.key == pygame.K_c:
                        start = grid[2][2]
                        end = grid[ROWS-3][ROWS-3]
                        for row in grid:
                            for node in row:
                                node.reset()
                        start.make_start()
                        end.make_end()
                    if event.key == pygame.K_m:
                        generate_random_maze(grid, start, end, 0.3)
                    
                    if event.key == pygame.K_SPACE:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        
                        # Clear previous paths/visited nodes but keep walls
                        for row in grid:
                            for node in row:
                                if node.color in [RED, YELLOW, GREEN]:
                                    node.reset()

                        agent_path, nodes, exec_time = find_path(lambda: draw_main(WIN, grid, ROWS, GRID_WIDTH, metrics, config), grid, start, end, config['algo'], config['heuristic'])
                        
                        if agent_path:
                            metrics['nodes'] = nodes
                            metrics['cost'] = len(agent_path)
                            metrics['time'] = exec_time
                            
                            # Trigger agent movement mode
                            is_agent_moving = True
                            agent_pos_index = 0

    pygame.quit()

if __name__ == "__main__":
    main()