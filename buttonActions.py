from typing import Callable, Optional, Dict
import pygame

import config
from button import Button
from grid import Grid, algorithms, cellTypes

import asyncio

# Helper function to reset all buttons except the one passed in (and the algorithm buttons)
def reset_all_buttons(buttons: Dict[str, Button], exception: str):
    for button_key, button in buttons.items():
        if button_key != exception and not button_key.startswith('algorithm_'):
            button.clicked = False
            button.updated = True

def reset_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Reset button clicked")
    buttonName = 'reset'
    
    reset_all_buttons(buttons, buttonName)
    
    pathingGrid.cancelled = False
    
    # If clicked for the first time, reset only checked and path cells; keep walls and start/end points
    if not buttons[buttonName].clicked:
        for row in range(pathingGrid.rows):
            for col in range(pathingGrid.cols):
                if pathingGrid.cells[row][col] == cellTypes["checked"] or pathingGrid.cells[row][col] == cellTypes["path"]:
                    pathingGrid.cells[row][col] = cellTypes["empty"]
        buttons[buttonName].clicked = True
        buttons[buttonName].updated = True
        return
    
    # Else, reset the grid
    pathingGrid.cells = [[0 for _ in range(pathingGrid.cols)] for _ in range(pathingGrid.rows)]
            
    # Reset start and end points
    if hasattr(pathingGrid, 'start'): del pathingGrid.start
    if hasattr(pathingGrid, 'end'): del pathingGrid.end
    
def set_start_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Set start button clicked")
    buttonName = 'setStart'
    
    reset_all_buttons(buttons, buttonName)
    
def set_end_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Set end button clicked")
    buttonName = 'setEnd'
    
    reset_all_buttons(buttons, buttonName)
    
def draw_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Draw button clicked")
    buttonName = 'draw'
    
    reset_all_buttons(buttons, buttonName)
            
def pathing_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Pathing button clicked")
    buttonName = 'pathing'
    
    # Check if start and end points are set
    if not hasattr(pathingGrid, 'start') or not hasattr(pathingGrid, 'end'):
        if config.LOGGING: print("Start and end points not set")
        return
    
    # Set all other buttons to not clicked using the list
    for button_key, button in buttons.items():
        if button_key != buttonName and not button_key.startswith('algorithm_'):
            button.clicked = False
            button.active = False
            button.updated = True
            
    buttons['cancel'].active = True
    buttons['pathing'].active = False
    buttons['cancel'].visible = True
    buttons['followPath'].active = True
    
    if pathingGrid.algorithm == algorithms['A*']:
        asyncio.create_task(pathingGrid.find_path_Astar())
    elif pathingGrid.algorithm == algorithms['Dijkstra']:
        asyncio.create_task(pathingGrid.find_path_Dijkstra())
    elif pathingGrid.algorithm == algorithms['BFS']:
        asyncio.create_task(pathingGrid.find_path_BFS())
    elif pathingGrid.algorithm == algorithms['DFS']:
        asyncio.create_task(pathingGrid.find_path_DFS())
    
def cancel_action(buttons: Dict[str, Button], grid: Grid):
    if config.LOGGING: print("Cancel button clicked")
    buttonName = 'cancel'
    
    # Set all other buttons to not clicked using the list
    for button_key, button in buttons.items():
        if button_key != buttonName and not button_key.startswith('algorithm_'):
            button.clicked = False
            button.active = True
            button.updated = True
    
    # Set the cancelled flag
    grid.cancelled = True
    buttons['cancel'].visible = False
    
def benchmark_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Benchmark button clicked")
    buttonName = 'benchmark'
    
    reset_all_buttons(buttons, buttonName)
            
    # Reset the grid
    reset_action(buttons, pathingGrid)
    
    # Set up the benchmark level
    pathingGrid.create_benchmark_level()
    
    # Start the benchmark
    pathingGrid.benchmark = True
    pathing_action(buttons, pathingGrid)
    
def set_algorithm_action(buttons: Dict[str, Button], pathingGrid: Grid, algorithm: str):
    working = buttons["cancel"].visible
    
    for button_key, button in buttons.items():
        if button_key.startswith('algorithm_'):
            if not working:
                button.clicked = False
                button.updated = True
                
    # TODO: Algorithm buttons should be disabled when pathing is in progress
            
    buttons[f'algorithm_{algorithm}'].clicked = True
    
    # Set the algorithm
    pathingGrid.algorithm = algorithms[algorithm]
    if config.LOGGING: print(f"Algorithm set to {algorithm}")
    
def create_maze_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Create Maze button clicked")
    buttonName = 'createMaze'
    
    reset_all_buttons(buttons, buttonName)
    
    # Reset the grid
    reset_action(buttons, pathingGrid)
    
    # Create the maze
    pathingGrid.create_maze()
    
def follow_path_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Follow Path button clicked")
    buttonName = 'followPath'
    
    if not buttons["cancel"].visible:
        print("No path constructed yet")
        return
    
    # Follow the path
    pathingGrid.follow_path()