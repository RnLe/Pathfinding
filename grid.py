from typing import Callable, Optional, Dict
import pygame

import time
import json
from math import sqrt

from button import Button
import config

import asyncio
import random

import sys
sys.setrecursionlimit(100000)  # Set new recursion limit

random.seed(42)

# Constants
cellTypes = {"empty": 0, "wall": 1, "path": 2, "checked": 3, "start": 4, "end": 5, "tree": 11, "rocks": 12}
algorithms = {"A*": 0, "Dijkstra": 1, "BFS": 2, "DFS": 3}

class Grid:
    def __init__(self, x, y, width, height, rows, cols, screen, start=None, end=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.cell_width = width // cols
        self.cell_height = height // rows
        self.cells = [[0 for _ in range(cols)] for _ in range(rows)]
        self.cancelled = False
        self.benchmark = False
        self.benchmarkLevel = ""
        self.algorithm = algorithms["A*"]
        self.rect = pygame.Rect(x, y, width, height)
        self.updatedAreas = [self.rect]
        
        self.screen = screen
        
        # pre-defined colors for the grid cells
        # 0: white (empty cell), 1: black (wall cell), 2: green (path cell), 3: yellow (checked cell), 4: blue (start cell), 5: red (end cell)
        self.colors = ((255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 0))
        
        # Pre-define surfaces for grid cells
        self.cellSize = (self.cell_width, self.cell_height)
        
        self.emptyCell = pygame.Surface(self.cellSize)
        self.emptyCell.fill(self.colors[0])
        self.wallCell = pygame.Surface(self.cellSize)
        self.wallCell.fill(self.colors[1])
        self.pathCell = pygame.Surface(self.cellSize)
        self.pathCell.fill(self.colors[2])
        self.checkedCell = pygame.Surface(self.cellSize)
        self.checkedCell.fill(self.colors[3])
        self.startCell = pygame.Surface(self.cellSize)
        self.startCell.fill(self.colors[4])
        self.endCell = pygame.Surface(self.cellSize)
        self.endCell.fill(self.colors[5])
        
        self.hLine = pygame.Surface((self.width, 1))
        self.hLine.fill((200, 200, 200))
        self.vLine = pygame.Surface((1, self.height))
        self.vLine.fill((200, 200, 200))
        
        # Load images
        self.tree_image = pygame.image.load('sprites/tree_spruce.png').convert_alpha()
        self.rocks_image = pygame.image.load('sprites/rocks.png').convert_alpha()
        # Get size of the image
        self.tree_size = self.tree_image.get_size()
        self.rocks_size = self.rocks_image.get_size()
        # Scale the image to the cell size + 10% padding
        self.tree_image = pygame.transform.scale(self.tree_image, (int(self.cell_width * 1.1), int(self.cell_height * 1.1)))
        self.rocks_image = pygame.transform.scale(self.rocks_image, (int(self.cell_width * 1.1), int(self.cell_height * 1.1)))
    
    def get_cell_rect(self, pos):
        # Pos is not the cursor position, but the position of the cell in the grid
        i, j = pos
        if 0 <= i < self.rows and 0 <= j < self.cols:
            return pygame.Rect(self.x + j * self.cell_width, self.y + i * self.cell_height, self.cell_width, self.cell_height)
        return None
        
    def set_start(self, pos):
        self.start = pos
        self.updatedAreas.append(self.get_cell_rect(pos))
    
    def set_end(self, pos):
        self.end = pos
        self.updatedAreas.append(self.get_cell_rect(pos))

    def draw(self, surface):
       
        for i in range(self.rows):
            for j in range(self.cols):
                # Determine position of cell
                cell_position = (j * self.cell_width, i * self.cell_height)
                
                if self.cells[i][j] == cellTypes["empty"]:
                    surface.blit(self.emptyCell, (self.x + cell_position[0], self.y + cell_position[1]))
                elif self.cells[i][j] == cellTypes["tree"]:
                    surface.blit(self.rocks_image, (self.x + cell_position[0], self.y + cell_position[1]))
                elif self.cells[i][j] == cellTypes["rocks"]:
                    surface.blit(self.tree_image, (self.x + cell_position[0], self.y + cell_position[1]))
                elif self.cells[i][j] == cellTypes["path"]:
                    surface.blit(self.pathCell, (self.x + cell_position[0], self.y + cell_position[1]))
                elif self.cells[i][j] == cellTypes["checked"]:
                    surface.blit(self.checkedCell, (self.x + cell_position[0], self.y + cell_position[1]))
                
        # Draw fine grid lines for the grid
        for i in range(self.rows + 1):
            surface.blit(self.hLine, (self.x, self.y + i * self.cell_height))
        for j in range(self.cols + 1):
            surface.blit(self.vLine, (self.x + j * self.cell_width, self.y))
            
        # Draw start and end points if set
        if hasattr(self, 'start'):
            # Start point
            surface.blit(self.startCell, (self.x + self.start[1] * self.cell_width, self.y + self.start[0] * self.cell_height))
            
        if hasattr(self, 'end'):
            # End point
            surface.blit(self.endCell, (self.x + self.end[1] * self.cell_width, self.y + self.end[0] * self.cell_height))

    def handle_event(self, event: pygame.event.Event, buttons: Dict[str, Button]):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check whether start or end button is clicked
            if buttons['setStart'].clicked:
                i = (event.pos[1] - self.y) // self.cell_height
                j = (event.pos[0] - self.x) // self.cell_width
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    self.set_start((i, j))
                    buttons['setStart'].clicked = False
            elif buttons['setEnd'].clicked:
                i = (event.pos[1] - self.y) // self.cell_height
                j = (event.pos[0] - self.x) // self.cell_width
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    self.set_end((i, j))
                    buttons['setEnd'].clicked = False
            elif buttons['draw'].clicked:
                self.draw_cell(event.pos)
        # Check whether the mouse is moving while the left mouse button is pressed
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] and buttons['draw'].clicked:
            # Draw the cell under the mouse cursor
            self.draw_cell(event.pos)
            
    def draw_cell(self, pos):
        i = (pos[1] - self.y) // self.cell_height
        j = (pos[0] - self.x) // self.cell_width
        if 0 <= i < self.rows and 0 <= j < self.cols:
            # Randomly set either a tree or rocks, if cell is empty
            if self.cells[i][j] == cellTypes["empty"]:
                self.cells[i][j] = cellTypes["tree"] if random.random() < 0.5 else cellTypes["rocks"]
                self.updatedAreas.append(self.get_cell_rect((i, j)))
            
    def heuristic(self, node, end):
        # Heuristik: Manhattandistanz zum Endknoten
        return abs(node[0] - end[0]) + abs(node[1] - end[1])
            
    async def find_path_Astar(self):
        # Start timer
        start_time = time.time()
        
        open_list = set([self.start])
        closed_list = set()

        g = {self.start: 0}
        parents = {self.start: self.start}
        
        print(open_list, closed_list, g, parents)

        while len(open_list) > 0 and not self.cancelled:
            current = min(open_list, key=lambda x: g[x] + self.heuristic(x, self.end))
            
            if current == self.end:
                self.reconstruct_path(parents, self.end)
                pathTime = (time.time() - start_time)*1000
                print(f"Time: {pathTime} ms")
                print("Pfad gefunden")
                if self.benchmark:
                    self.benchmark = False
                    if config.SAVE_BENCHMARKS:
                        self.saveBenchmark(pathTime)
                return

            open_list.remove(current)
            closed_list.add(current)
            # Set cell to checked if it is empty
            if self.cells[current[0]][current[1]] == cellTypes["empty"]:
                self.cells[current[0]][current[1]] = cellTypes["checked"]
                self.updatedAreas.append(self.get_cell_rect(current))

            neighbors, costs = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue
                if neighbor not in open_list:
                    open_list.add(neighbor)

                tentative_g_score = g[current] + costs[neighbor]  # Assuming each step costs 1
                if tentative_g_score >= g.get(neighbor, float('inf')):
                    continue

                # This path is the best so far, record it
                parents[neighbor] = current
                g[neighbor] = tentative_g_score
            
            await asyncio.sleep(0)
            
            if self.cancelled:
                print("Pathfinding cancelled.")
                return
                

        print("No path found")
        print(f"Time: {(time.time() - start_time)*1000} ms")
        
    async def find_path_Dijkstra(self):
        # Start timer
        start_time = time.time()

        open_list = set([self.start])
        closed_list = set()

        # Kosten vom Startknoten zu einem Knoten
        g = {self.start: 0}
        parents = {self.start: self.start}

        while open_list and not self.cancelled:
            # Wähle den Knoten mit den geringsten Kosten
            current = min(open_list, key=lambda x: g[x])

            if current == self.end:
                self.reconstruct_path(parents, self.end)
                pathTime = (time.time() - start_time) * 1000
                print(f"Time: {pathTime} ms")
                print("Pfad gefunden")
                if self.benchmark:
                    self.benchmark = False
                    if config.SAVE_BENCHMARKS:
                        self.saveBenchmark(pathTime)
                return

            open_list.remove(current)
            closed_list.add(current)
            
            # Set cell to checked if it is empty
            if self.cells[current[0]][current[1]] == cellTypes["empty"]:
                self.cells[current[0]][current[1]] = cellTypes["checked"]

            neighbors, costs = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue

                tentative_g_score = g[current] + costs[neighbor]  # Kosten für den Schritt, typischerweise 1 in einem Raster

                if neighbor not in open_list:
                    open_list.add(neighbor)
                elif tentative_g_score >= g.get(neighbor, float('inf')):
                    continue  # Dieser neue Pfad ist nicht besser als der vorhandene

                # Dieser Pfad ist der beste bisher, speichere ihn
                parents[neighbor] = current
                g[neighbor] = tentative_g_score

            await asyncio.sleep(0)

            if self.cancelled:
                print("Pathfinding abgebrochen.")
                return

        print("Kein Pfad gefunden")
        print(f"Time: {(time.time() - start_time) * 1000} ms")
    
    async def find_path_BFS(self):
        # Start timer
        start_time = time.time()

        # Initialisiere eine Warteschlange mit dem Startknoten
        queue = [self.start]
        visited = set([self.start])

        parents = {self.start: self.start}

        while queue and not self.cancelled:
            current = queue.pop(0)
            # Set cell to checked if it is empty
            if self.cells[current[0]][current[1]] == cellTypes["empty"]:
                self.cells[current[0]][current[1]] = cellTypes["checked"]

            if current == self.end:
                self.reconstruct_path(parents, self.end)
                pathTime = (time.time() - start_time) * 1000
                print(f"Time: {pathTime} ms")
                print("Path found!")
                if self.benchmark:
                    self.benchmark = False
                    if config.SAVE_BENCHMARKS:
                        self.saveBenchmark(pathTime)
                return

            neighbors, costs = self.get_neighbors(current, diagonals=False)
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parents[neighbor] = current

            await asyncio.sleep(0)

            if self.cancelled:
                print("Pathfinding cancelled")
                return

        print("No path found")
        print(f"Time: {(time.time() - start_time) * 1000} ms")
    
    async def find_path_DFS(self):
        # Start timer
        start_time = time.time()

        # Initialisiere einen Stapel mit dem Startknoten
        stack = [self.start]
        visited = set([self.start])

        parents = {self.start: self.start}

        while stack and not self.cancelled:
            current = stack.pop()  # Letzten Knoten vom Stapel nehmen

            # Zelle als untersucht markieren, wenn sie leer ist
            if self.cells[current[0]][current[1]] == cellTypes["empty"]:
                self.cells[current[0]][current[1]] = cellTypes["checked"]

            if current == self.end:
                self.reconstruct_path(parents, self.end)
                pathTime = (time.time() - start_time) * 1000
                print(f"Time: {pathTime} ms")
                print("Pfad gefunden")
                if self.benchmark:
                    self.benchmark = False
                    if config.SAVE_BENCHMARKS:
                        self.saveBenchmark(pathTime)
                return

            neighbors, costs = self.get_neighbors(current, diagonals=False)
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append(neighbor)  # Füge den Nachbarn zum Stapel hinzu
                    visited.add(neighbor)
                    parents[neighbor] = current

            await asyncio.sleep(0)

            if self.cancelled:
                print("Pathfinding abgebrochen.")
                return

        print("Kein Pfad gefunden")
        print(f"Time: {(time.time() - start_time) * 1000} ms")
        
        
    def cancel_pathfinding(self):
        self.cancelled = True

    def reconstruct_path(self, parents, end):
        path = []
        current = end
        while parents[current] != current:
            path.append(current)
            current = parents[current]
        path.append(self.start)  # optional
        path.reverse()  # optional
        self.draw_path(path)
        print(f"Lenght of the path: {len(path)}")

    def get_neighbors(self, node, diagonals=True):
        neighbors = []
        costs = {}
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                new_row, new_col = node[0] + i, node[1] + j
                # Check grid boundaries
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    # Check if cell is empty (or checked)
                    if self.cells[new_row][new_col] == cellTypes["empty"] or self.cells[new_row][new_col] == cellTypes["checked"]:
                        # Always add orthogonal neighbors with cost of 1
                        if i == 0 or j == 0:
                            neighbors.append((new_row, new_col))
                            costs[(new_row, new_col)] = 1
                        elif diagonals:
                            # For diagonal neighbors, check if the orthogonal neighbors are empty
                            # Diagonal neighbors get a cost of sqrt(2)
                            adj_1 = self.cells[node[0] + i][node[1]]
                            adj_2 = self.cells[node[0]][node[1] + j]
                            if adj_1 == cellTypes["empty"] or adj_2 == cellTypes["empty"] or adj_1 == cellTypes["checked"] or adj_2 == cellTypes["checked"]:
                                neighbors.append((new_row, new_col))
                            costs[(new_row, new_col)] = sqrt(2)
        return neighbors, costs

    
    def draw_path(self, path):
        # Drop the start and end points
        path = path[1:-1]
        # Draw path by
        for node in path:
            self.cells[node[0]][node[1]] = cellTypes["path"]
            self.updatedAreas.append(self.get_cell_rect(node))
            
    def create_benchmark_level(self):
        # Version 1. Add more benchmark levels later
        # Start at the top left corner, end at the bottom right corner, and a diagonal line perpendicularly in the middle, excluding the top right and bottom left corners
        self.start = (0, 0)
        self.end = (self.rows - 1, self.cols - 1)
        
        # IMPORTANT: !ASSUMING A SQUARE GRID!
        for i in range(self.rows - 1):
            self.cells[i][self.rows - i - 1] = cellTypes["tree"] if random.random() < 0.5 else cellTypes["rocks"]
            self.updatedAreas.append(pygame.Rect(self.x + (self.rows - i - 1) * self.cell_width, self.y + i * self.cell_height, self.cell_width, self.cell_height))
            
        self.benchmarkLevel = "v000"
            
    def saveBenchmark(self, pathTime: float):
        # Save the benchmark level, datetime and time to a JSON file
        data = {
            "level": self.benchmarkLevel,
            "algorithm": next(key for key, value in algorithms.items() if value == self.algorithm),
            "rows": self.rows,
            "cols": self.cols,
            "fps": config.FPS,
            "programmVersion": "v0.4",
            "recentChanges": "Optimized main loop and capped FPS to 100, giving the logic more time to run before updating the screen.",
            "time": pathTime,
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("benchmarking/benchmark.json", "a") as f:
            f.write(json.dumps(data) + "\n")
    
    def second_neighbors(self, node):
        """Function to get the second neighbors of a node, counting only orthogonal, filled cells

        Args:
            node (tuple): Center node

        Returns:
            neighbors (list(tuple)): List of second neighbors
        """        
        neighbors = []
        for i in range(-2, 3, 2):
            for j in range(-2, 3, 2):
                # Skip self and diagonals
                if i == 0 and j == 0 or i != 0 and j != 0:
                    continue
                new_row, new_col = node[0] + i, node[1] + j
                # Check grid boundaries
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    # Check if cell is not empty
                    if self.cells[new_row][new_col] == cellTypes["tree"]:
                        neighbors.append((new_row, new_col))
        return neighbors
            
    def create_maze(self):
        # Create a maze using the recursive backtracking algorithm
        # Start with a grid full of walls
        # There are no "walls", just empty of filled cells
        self.cells = [[cellTypes["tree"] for _ in range(self.cols)] for _ in range(self.rows)]
        # Start at the top left corner
        start = (1, 1)
        self.start = start
        self.end = (self.rows - 1, self.cols - 1)
        # Create the maze
        self.recursive_backtracking(start)

    def recursive_backtracking(self, current):
        # Set the current cell to empty
        self.cells[current[0]][current[1]] = cellTypes["empty"]
        # Get the neighbors of the current cell
        neighbors = self.second_neighbors(current)
        # Randomize the order of the neighbors
        random.shuffle(neighbors)
        for neighbor in neighbors:
            if self.cells[neighbor[0]][neighbor[1]] == cellTypes["tree"]:
                # Get the cell in between the current and the neighbor
                between = ((current[0] + neighbor[0]) // 2, (current[1] + neighbor[1]) // 2)
                # Set the cell in between to empty
                self.cells[between[0]][between[1]] = cellTypes["empty"]
                # Recursively call the function with the neighbor as the current cell
                self.recursive_backtracking(neighbor)
