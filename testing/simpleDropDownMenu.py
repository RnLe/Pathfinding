import pygame
import sys

pygame.init()

# Bildschirmeinstellungen
screen = pygame.display.set_mode((200, 140))
pygame.display.set_caption("Dropdown-Menü Beispiel")

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
LIGHT_GREY = (220, 220, 220)

# Dropdown-Menü Einstellungen
menu_font = pygame.font.SysFont(None, 30)
dropdown_items = ["Option 1", "Option 2", "Option 3"]
item_height = 35
menu_open = False
main_button_rect = pygame.Rect(0, 0, 200, item_height)
dropdown_rects = []

# Text für den Hauptbutton
main_button_text = "Wähle eine Option"

# Hauptschleife
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if main_button_rect.collidepoint(event.pos):
                menu_open = not menu_open  # Menü umschalten
            elif menu_open:
                for i, rect in enumerate(dropdown_rects):
                    if rect.collidepoint(event.pos):
                        main_button_text = dropdown_items[i]  # Auswahl aktualisieren
                        menu_open = False  # Menü schließen
                        break

    # Hauptbutton zeichnen
    pygame.draw.rect(screen, LIGHT_GREY, main_button_rect)
    text_surf = menu_font.render(main_button_text, True, BLACK)
    screen.blit(text_surf, (main_button_rect.x + 5, main_button_rect.y + 5))

    # Dropdown-Elemente zeichnen, wenn das Menü geöffnet ist
    dropdown_rects = []
    if menu_open:
        for i, item in enumerate(dropdown_items):
            rect = pygame.Rect(main_button_rect.x, main_button_rect.y + (i + 1) * item_height, main_button_rect.width, item_height)
            pygame.draw.rect(screen, GREY, rect)
            text_surf = menu_font.render(item, True, BLACK)
            screen.blit(text_surf, (rect.x + 5, rect.y + 5))
            dropdown_rects.append(rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
