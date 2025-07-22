import pygame
import sys

# Start pygame
pygame.init()

# Window Settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60

# Map settings - Alex
TILE_SIZE = 40
MAP_COLS = WINDOW_WIDTH // TILE_SIZE
MAP_ROWS = WINDOW_HEIGHT // TILE_SIZE
# 0 = empty, 1 = wall 
game_map = []
for row in range(MAP_ROWS):
    if row == 0 or row == MAP_ROWS - 1:
        game_map.append([1] * MAP_COLS)
    else:
        game_map.append([1] + [0] * (MAP_COLS - 2) + [1])

# Create window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Draw map - Alex
    for row_idx, row in enumerate(game_map):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (100, 100, 100), rect)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()