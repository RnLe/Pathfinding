# Class to create an entity object. This entity can move around the grid and find paths to other entities.

import pygame
from grid import Grid
from button import Button
from functools import partial
import buttonActions

class Entity:
    def __init__(self, x, y, grid, color):
        self.x = x
        self.y = y
        self.grid = grid
        self.color = color
        self.path = []
        self.pathingAlgorithm = "A*"
        
    