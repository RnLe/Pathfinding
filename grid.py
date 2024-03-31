from typing import Callable, Optional, Dict
import pygame

import time

from button import Button

import asyncio

# TODO: Optimize drawing of grid cells and remove redundancies (e.g. draw grid lines only once)

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
        
        self.screen = screen
        
    def set_start(self, pos):
        self.start = pos
    
    def set_end(self, pos):
        self.end = pos

    def draw(self, surface):
        for i in range(self.rows):
            for j in range(self.cols):
                color = (255, 255, 255)
                if self.cells[i][j] == 1:
                    # Empty cell
                    color = (0, 0, 0)
                elif self.cells[i][j] == 2:
                    # Path cell (green)
                    color = (0, 255, 0)
                elif self.cells[i][j] == 3:
                    # Checked cell (yellow)
                    color = (255, 255, 0)
                pygame.draw.rect(surface, color, (self.x + j * self.cell_width, self.y + i * self.cell_height, self.cell_width, self.cell_height))
        # Draw fine grid lines for the grid
        for i in range(self.rows + 1):
            pygame.draw.line(surface, (200, 200, 200), (self.x, self.y + i * self.cell_height), (self.x + self.width, self.y + i * self.cell_height))
        for j in range(self.cols + 1):
            pygame.draw.line(surface, (200, 200, 200), (self.x + j * self.cell_width, self.y), (self.x + j * self.cell_width, self.y + self.height))
            
        # Draw start and end points if set
        if hasattr(self, 'start'):
            # Blue start point
            startColor = (0, 0, 255)
            pygame.draw.rect(surface, startColor, (self.x + self.start[1] * self.cell_width, self.y + self.start[0] * self.cell_height, self.cell_width, self.cell_height))
            
        if hasattr(self, 'end'):
            # Red end point
            endColor = (255, 0, 0)
            pygame.draw.rect(surface, endColor, (self.x + self.end[1] * self.cell_width, self.y + self.end[0] * self.cell_height, self.cell_width, self.cell_height))

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
                self.draw_cell(event.pos, True)
        # Check whether the mouse is moving while the left mouse button is pressed
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] and buttons['draw'].clicked:
            # Draw the cell under the mouse cursor
            self.draw_cell(event.pos, True)
            
    def draw_cell(self, pos:int, state:bool):
        i = (pos[1] - self.y) // self.cell_height
        j = (pos[0] - self.x) // self.cell_width
        if 0 <= i < self.rows and 0 <= j < self.cols:
            self.cells[i][j] = state
            
    def heuristic(self, node, end):
        # Heuristik: Manhattandistanz zum Endknoten
        return abs(node[0] - end[0]) + abs(node[1] - end[1])
            
    async def find_path(self):
        # Start timer
        start_time = time.time()
        
        open_list = set([self.start])
        closed_list = set()

        g = {self.start: 0}
        parents = {self.start: self.start}

        while len(open_list) > 0 and not self.cancelled:
            current = min(open_list, key=lambda x: g[x] + self.heuristic(x, self.end))
            
            if current == self.end:
                self.reconstruct_path(parents, self.end)
                print(f"Time: {(time.time() - start_time)*1000} ms")
                print("Pfad gefunden")
                return

            open_list.remove(current)
            closed_list.add(current)
            # Set cell to checked
            self.cells[current[0]][current[1]] = 3

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_list:
                    continue
                if neighbor not in open_list:
                    open_list.add(neighbor)

                tentative_g_score = g[current] + 1  # Assuming each step costs 1
                if tentative_g_score >= g.get(neighbor, float('inf')):
                    continue

                # This path is the best so far, record it
                parents[neighbor] = current
                g[neighbor] = tentative_g_score
            
            await asyncio.sleep(0)
            
            if self.cancelled:
                print("Pathfinding cancelled.")
                return
                

        print("Kein Pfad gefunden")
        print(f"Time: {(time.time() - start_time)*1000} ms")
        
        
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

    def get_neighbors(self, node):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                new_row, new_col = node[0] + i, node[1] + j
                # Check grid boundaries
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    
                    if self.cells[new_row][new_col] == 0:
                        # Always add orthogonal neighbors
                        if i == 0 or j == 0:
                            neighbors.append((new_row, new_col))
                        else:
                            # For diagonal neighbors, check if the orthogonal neighbors are empty
                            adj_1 = self.cells[node[0] + i][node[1]]
                            adj_2 = self.cells[node[0]][node[1] + j]
                            if adj_1 == 0 and adj_2 == 0:
                                neighbors.append((new_row, new_col))
        return neighbors

    
    def draw_path(self, path):
        # Draw path by
        for node in path:
            self.cells[node[0]][node[1]] = 2
            
    
                