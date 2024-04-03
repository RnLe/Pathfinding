import pygame

from functools import partial       # Standard library function to create partial (pre-filled) functions

import config
from button import Button
from grid import Grid
import buttonActions

import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    # Set the window title
    pygame.display.set_caption("Pathfinding")

    # GUI left panel
    panel = pygame.Surface((200, 800))
    panel.fill((30, 30, 30))
    
    # Settings
    rows = 100
    cols = 100

    # Grid
    pathingGrid = Grid(200, 0, 800, 800, rows, cols, screen)    

    buttons = {}

    # Wrapper functions for button actions
    reset_action_w = partial(buttonActions.reset_action, buttons, pathingGrid)
    set_start_action_w = partial(buttonActions.set_start_action, buttons)
    set_end_action_w = partial(buttonActions.set_end_action, buttons)
    draw_action_w = partial(buttonActions.draw_action, buttons)
    pathing_action_w = partial(buttonActions.pathing_action, buttons, pathingGrid)
    cancel_action_w = partial(buttonActions.cancel_action, buttons, pathingGrid)
    benchmark_action_w = partial(buttonActions.benchmark_action, buttons, pathingGrid)
    # Algorithm buttons (names must match dictionary in grid.py)
    aStar_action_w = partial(buttonActions.set_algorithm, buttons, pathingGrid, 'A*')
    dijkstra_action_w = partial(buttonActions.set_algorithm, buttons, pathingGrid, 'Dijkstra')
    breadthFirst_action_w = partial(buttonActions.set_algorithm, buttons, pathingGrid, 'BFS')
    depthFirst_action_w = partial(buttonActions.set_algorithm, buttons, pathingGrid, 'DFS')    

    # Buttons
    resetButton = Button(10, 5, 180, 50, "Reset", reset_action_w)
    setStartButton = Button(10, 60, 180, 50, "Set Start", set_start_action_w, toggle=True)
    setEndButton = Button(10, 115, 180, 50, "Set End", set_end_action_w, toggle=True)
    drawButton = Button(10, 170, 180, 50, "Draw", draw_action_w, toggle=True)
    pathingButton = Button(10, 225, 180, 50, "Pathing", pathing_action_w)
    cancelPathingButton = Button(10, 280, 180, 50, "Cancel", cancel_action_w, visible=False)
    benchmarkButton = Button(10, 335, 180, 50, "Benchmark", benchmark_action_w)
    # 4 Smaller buttons with half width (same height) for the algorithms
    aStarButton = Button(10, 390, 85, 50, "A*", aStar_action_w, toggle=True, clicked=True)
    dijkstraButton = Button(105, 390, 85, 50, "Dijkstra", dijkstra_action_w, toggle=True)
    breadthFirstButton = Button(10, 445, 85, 50, "BFS", breadthFirst_action_w, toggle=True)
    depthFirstButton = Button(105, 445, 85, 50, "DFS", depthFirst_action_w, toggle=True)

    # Add to dictionary
    buttons['reset'] = resetButton
    buttons['setStart'] = setStartButton
    buttons['setEnd'] = setEndButton
    buttons['draw'] = drawButton
    buttons['pathing'] = pathingButton
    buttons['cancel'] = cancelPathingButton
    buttons['benchmark'] = benchmarkButton
    # Algorithm buttons need to start with "algorithm_"
    buttons['algorithm_A*'] = aStarButton
    buttons['algorithm_Dijkstra'] = dijkstraButton
    buttons['algorithm_BFS'] = breadthFirstButton
    buttons['algorithm_DFS'] = depthFirstButton

    # Main loop
    ############################
    running = True
    fps = config.FPS

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Group events by type (mouse, keyboard, etc.)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for (key, button) in buttons.items():
                    button.handle_event(event)
                pathingGrid.handle_event(event, buttons)
            if event.type == pygame.KEYDOWN:
                pass
            if event.type == pygame.MOUSEMOTION:
                pathingGrid.handle_event(event, buttons)
            
        screen.fill((255, 255, 255))
        screen.blit(panel, (0, 0))
        
        # Draw buttons
        for button in buttons.values():
            if button.visible:
                button.draw(screen)
        
        pathingGrid.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(1/fps)

    
    # Quit pygame
    pygame.quit()
    
asyncio.run(main())