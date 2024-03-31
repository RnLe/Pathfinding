from typing import TypedDict, Dict
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

    # Grid
    pathingGrid = Grid(200, 0, 800, 800, 100, 100, screen)

    # Add all buttons to a dictionary (TypedDict for intellisense)
    class ButtonDict(TypedDict):
        reset: Button
        setStart: Button
        setEnd: Button
        draw: Button
        pathing: Button
        cancel: Button

    buttons: ButtonDict = {}

    # Wrapper functions for button actions
    reset_action_w = partial(buttonActions.reset_action, pathingGrid)
    set_start_action_w = partial(buttonActions.set_start_action, buttons)
    set_end_action_w = partial(buttonActions.set_end_action, buttons)
    draw_action_w = partial(buttonActions.draw_action, buttons)
    pathing_action_w = partial(buttonActions.pathing_action, buttons, pathingGrid)
    cancel_action_w = partial(buttonActions.cancel_action, buttons, pathingGrid)

    # Buttons
    resetButton = Button(10, 5, 180, 50, "Reset", reset_action_w)
    setStartButton = Button(10, 60, 180, 50, "Set Start", set_start_action_w, toggle=True)
    setEndButton = Button(10, 115, 180, 50, "Set End", set_end_action_w, toggle=True)
    drawButton = Button(10, 170, 180, 50, "Draw", draw_action_w, toggle=True)
    pathingButton = Button(10, 225, 180, 50, "Pathing", pathing_action_w)
    cancelPathingButton = Button(10, 280, 180, 50, "Cancel", cancel_action_w)

    # Add to dictionary
    buttons['reset'] = resetButton
    buttons['setStart'] = setStartButton
    buttons['setEnd'] = setEndButton
    buttons['draw'] = drawButton
    buttons['pathing'] = pathingButton
    buttons['cancel'] = cancelPathingButton

    # Main loop
    ############################
    running = True

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
            button.draw(screen)
        
        pathingGrid.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0)

    
    # Quit pygame
    pygame.quit()
    
asyncio.run(main())