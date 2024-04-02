from typing import Callable, Optional
import pygame

import config

class Button:
    def __init__(self, x: int, y:int, width:int, height:int, text:str, onClick: Optional[Callable[[], None]] = None, toggle=False, visible: bool = True) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.onClick = onClick
        self.font = pygame.font.Font(None, 32)
        self.toggle = toggle
        self.clicked = False
        self.text_surf = self.font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.active = True
        self.visible = visible

    def draw(self, surface: pygame.Surface) -> None:
        # If a button is not visible, don't draw it
        if not self.visible: return
        # Set button color based on toggle state
        color = (100, 100, 100) if self.clicked else (200, 200, 200)
        if not self.active: color = (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        # If a button is not visible or active, don't handle events
        if not self.visible: return
        if not self.active: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.onClick:
                    if self.toggle: self.clicked = not self.clicked
                    self.onClick()