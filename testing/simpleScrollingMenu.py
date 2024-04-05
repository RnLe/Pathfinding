import pygame
import sys

# Pygame initialisieren
pygame.init()

# Bildschirmeinstellungen
screen = pygame.display.set_mode((220, 500))

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Menüelemente
menu_items = ["Item " + str(i) for i in range(100)]
item_height = 50
visible_items = 10
menu_height = visible_items * item_height

# Scroll-Variable
scroll_y = 0

# Hauptschleife
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            # Scrollen basierend auf Mausrad
            scroll_y += event.y * item_height
            scroll_y = min(scroll_y, 0)  # Verhindert das Scrollen nach oben über das erste Element hinaus
            scroll_y = max(scroll_y, -len(menu_items) * item_height + menu_height)  # Verhindert das Scrollen nach unten über das letzte Element hinaus
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                scroll_y += item_height
                scroll_y = min(scroll_y, 0)
            elif event.key == pygame.K_DOWN:
                scroll_y -= item_height
                scroll_y = max(scroll_y, -len(menu_items) * item_height + menu_height)
        # Bei gehaltener Maustaste auf die Scrollbar scrollen
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if 200 <= event.pos[0] <= 220:
                scrollbar_height = menu_height * visible_items / len(menu_items)
                scrollbar_y = -scroll_y * visible_items / len(menu_items)
                scroll_y = -event.pos[1] / visible_items * len(menu_items)
                scroll_y = min(scroll_y, 0)
                scroll_y = max(scroll_y, -len(menu_items) * item_height + menu_height)
    
    # Bildschirm löschen
    screen.fill(WHITE)
    
    # Menüelemente zeichnen
    for i, item in enumerate(menu_items):
        item_y = i * item_height + scroll_y
        if 0 <= item_y < menu_height:
            pygame.draw.rect(screen, GREY if i % 2 == 0 else WHITE, (0, item_y, 200, item_height))
            item_text = pygame.font.SysFont(None, 36).render(item, True, BLACK)
            screen.blit(item_text, (110, item_y + 10))
            
    # Zeichne Scrollbar
    pygame.draw.rect(screen, BLACK, (200, 0, 20, menu_height))
    scrollbar_height = menu_height * visible_items / len(menu_items)
    scrollbar_y = -scroll_y * visible_items / len(menu_items)
    pygame.draw.rect(screen, GREY, (200, scrollbar_y, 20, scrollbar_height))
    
    # Änderungen anzeigen
    pygame.display.flip()

pygame.quit()
sys.exit()
