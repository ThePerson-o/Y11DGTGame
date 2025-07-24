import pygame
import sys

# Start pygame
pygame.init()

# Window Settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60

# Map settings - Alex
TILE_SIZE = 40 # Sets the size of each tile
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

# Load background image
background_img = pygame.image.load("background.png")
background_img = pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))

#player - Riley
player = pygame.image.load('player.png').convert_alpha()
player = pygame.transform.scale(player, (100, 100))
player_pos = pygame.Vector2(90, 400)
player_rect = player.get_rect(center = player_pos)
player_vel = 4

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement - Riley
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= player_vel

    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += player_vel

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= player_vel

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += player_vel

    # update player rectangle position to player position
    player_rect.center = player_pos
    
    # Draw background image
    screen.blit(background_img, (0, 0))

    # Draw player
    screen.blit(player, player_rect)
    
    # Draw map - Alex
    for row_idx, row in enumerate(game_map):  # Loop through each row in the map
        for col_idx, tile in enumerate(row):  # Loop through each column (tile) in the row
            if tile == 1:  # If the tile is a wall
                rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)  # Create a rectangle for the wall tile
                pygame.draw.rect(screen, (100, 100, 100), rect)  # Draw the wall tile as a grey rectangle
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
<<<<<<< Updated upstream
sys.exit()
=======
sys.exit()  
>>>>>>> Stashed changes
