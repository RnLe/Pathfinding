# Class to create an entity object. This entity can move around the grid and find paths to other entities.

import pygame

class Entity:
    def __init__(self, x, y, grid, color, size):
        self.x = x
        self.y = y
        self.grid = grid
        self.color = color
        self.size = size
        self.path = []
        self.pathingAlgorithm = "A*"
        
    # TODO: Entities don't change the cell type. Thus they can't be detected by some code. Give them a type? Or maybe setup a class for entities (objects with physical properties) and turn this into a subclass of that class.
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 5)
    