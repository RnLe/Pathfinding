from typing import Callable, Optional, Dict
import pygame

import config
from button import Button
from grid import Grid

import asyncio

def reset_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Reset button clicked")
    # Reset the grid
    pathingGrid.cells = [[0 for _ in range(pathingGrid.cols)] for _ in range(pathingGrid.rows)]
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['reset']:
            button.clicked = False
            button.updated = True
            
    # Reset start and end points
    if hasattr(pathingGrid, 'start'): del pathingGrid.start
    if hasattr(pathingGrid, 'end'): del pathingGrid.end
    pathingGrid.cancelled = False
    
def set_start_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Set start button clicked")
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['setStart']:
            button.clicked = False
            button.updated = True
    
def set_end_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Set end button clicked")
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['setEnd']:
            button.clicked = False
            button.updated = True
    
def draw_action(buttons: Dict[str, Button]):
    if config.LOGGING: print("Draw button clicked")
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['draw']:
            button.clicked = False
            button.updated = True
            
def pathing_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Pathing button clicked")
    
    # Check if start and end points are set
    if not hasattr(pathingGrid, 'start') or not hasattr(pathingGrid, 'end'):
        if config.LOGGING: print("Start and end points not set")
        return
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['pathing']:
            button.clicked = False
            button.active = False
            button.updated = True
            
    buttons['cancel'].active = True
    buttons['pathing'].active = False
    buttons['cancel'].visible = True
    
    asyncio.create_task(pathingGrid.find_path())
    
def cancel_action(buttons: Dict[str, Button], grid: Grid):
    if config.LOGGING: print("Cancel button clicked")
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['cancel']:
            button.clicked = False
            button.active = True
            button.updated = True
    
    # Set the cancelled flag
    grid.cancelled = True
    buttons['cancel'].visible = False
    
def benchmark_action(buttons: Dict[str, Button], pathingGrid: Grid):
    if config.LOGGING: print("Benchmark button clicked")
    
    # Set all other buttons to not clicked using the list
    for button in buttons.values():
        if button != buttons['benchmark']:
            button.clicked = False
            button.updated = True
            
    # Reset the grid
    reset_action(buttons, pathingGrid)
    
    # Set up the benchmark level
    pathingGrid.create_benchmark_level()
    
    # Start the benchmark
    pathingGrid.benchmark = True
    pathing_action(buttons, pathingGrid)