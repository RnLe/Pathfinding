import pygame
import sys
import math

pygame.init()

# Bildschirmeinstellungen
screen = pygame.display.set_mode((200, 140))
pygame.display.set_caption("Dropdown-Menü Beispiel")
clock = pygame.time.Clock()

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
animation_progress = 0  # 0: Pfeil nach unten, 1: Pfeil nach oben

# Text für den Hauptbutton
main_button_text = "Choose"

def draw_arrow(surface, open_progress, rect):
    # Pfeilkoordinaten berechnen
    center_x = rect.right - 20
    center_y = rect.centery
    length = 10
    # Winkel von 0 bis 90 Grad; + einem kleinen Offset, um die Linien zu trennen
    angle = math.pi / 2 * open_progress + math.pi / 4

    # Linien für den Pfeil
    line1_start = (center_x - length * math.sin(angle), center_y - length * math.cos(angle))
    line1_end = (center_x, center_y)
    line2_start = (center_x + length * math.sin(angle), center_y - length * math.cos(angle))
    line2_end = line1_end

    pygame.draw.aaline(surface, BLACK, line1_start, line1_end, 1)
    pygame.draw.aaline(surface, BLACK, line2_start, line2_end, 1)

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
            
    # Animationsprogress aktualisieren
    if menu_open and animation_progress < 1:
        animation_progress += 0.1  # Geschwindigkeit der Animation anpassen
    elif not menu_open and animation_progress > 0:
        animation_progress -= 0.1

    animation_progress = max(0, min(1, animation_progress))  # Zwischen 0 und 1 begrenzen
    
    # Pfeil zeichnen
    draw_arrow(screen, animation_progress, main_button_rect)

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()
