import pygame
import sys

# Start pygame
pygame.init()


# Window Settings
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w - 10
WINDOW_HEIGHT = info.current_h - 10
FPS = 60

ZOOM = 1.2  # zoom level 

# Camera dead zone - Alex
CAMERA_MARGIN_X = 120
CAMERA_MARGIN_Y = 80

# Map settings - Alex
TILE_SIZE = 40 # Sets the size of each tile
MAP_COLS = WINDOW_WIDTH // TILE_SIZE 
MAP_ROWS = WINDOW_HEIGHT // TILE_SIZE
# 0 = empty, 1 = wall 
game_map = [] # Creates an empty list to store the map rows
for row in range(MAP_ROWS): # Loop every "Map Row"
    if row == 0 or row == MAP_ROWS - 1: # If it's the first or last row
        game_map.append([1] * MAP_COLS) # Fill the whole row with walls (1)
    else:
        game_map.append([1] + [0] * (MAP_COLS - 2) + [1]) # All other rows are empty (0)

# Create window BEFORE loading images to reduce gap in performance
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

# Load background image - Alex
background_img = pygame.image.load("background.png").convert_alpha()
BG_WIDTH, BG_HEIGHT = background_img.get_size()


#player - Riley
player = pygame.image.load('sprites/player.png').convert_alpha() # load the player image
player = pygame.transform.scale(player, (70, 70)) # set player size
player_pos = pygame.Vector2(100, 550) # set initial player position
player_rect = player.get_rect(center = player_pos) # Player rectangle for collisions
player_vel = 4 # player speed

# NPC - Alex
npc_img = pygame.image.load('sprites/NPC.png').convert_alpha()
npc_img = pygame.transform.scale(npc_img, (70, 70))
npc_pos = pygame.Vector2(BG_WIDTH // 2, BG_HEIGHT // 2)
npc_rect = npc_img.get_rect(center=npc_pos)

# projectiles - Riley
projectile_image = pygame.image.load('sprites/player_projectile.png').convert_alpha() # saves the projectile image
projectiles = [] # create a list to store information for projectiles (eg position)
projectile_vel = 2 # set the speed of the projectile

# Camera class for scrolling - Alex
## Deadzone means the position in the center where we keep the player
### pos.x and pos.y are the world coordinates
#### self.x and self.y are the camera's coordinates

class Camera:
    def __init__(self, width, height, bg_width, bg_height, zoom=1.0): # Sets the width height, etc.
        self.width = width
        self.height = height
        self.bg_width = bg_width
        self.bg_height = bg_height
        self.zoom = zoom
        self.x = 0 # starts at 0,0
        self.y = 0

    def update(self, target_pos): # Updates the camera position, self, to follow the player's position, target_pos

        # Find the center of the camera in world coordinates
        cam_cx = self.x + self.width // 2 # Give us the world position of the camera center
        cam_cy = self.y + self.height // 2

        # Calculate the distance from the target to the camera center
        dx = target_pos.x - cam_cx # dx and dy tell us how far the target is from the center. + is right, and - is left
        dy = target_pos.y - cam_cy

        # Is the camera outside the horizontal deadzone? 
        if abs(dx) > CAMERA_MARGIN_X: # Camera margin x is the buffer around the player
            self.x += dx - CAMERA_MARGIN_X * (1 if dx > 0 else -1) # moves the camera just enough so that the target sits at the edge of the dead zone
            # If dx = 150 and CAMERA_MARGIN_X = 100
                # Move camera by (150-100) = 50
            # If dx = 100 and CAMERA_MARGIN_X = 150
                # Move camera by (100-150) = -50
        
        # Is the camera outside the vertical deadzone?
        if abs(dy) > CAMERA_MARGIN_Y: # Same logic as x but vertical. 
            self.y += dy - CAMERA_MARGIN_Y * (1 if dy > 0 else -1) # same logic but vertical  

        # Clamp camera to background (To make sure that the camera doesn't show the blank space outside of the background)
        # 0,0 is top left
        max_x = self.bg_width - self.width # find x value of bottom right 
        max_y = self.bg_height - self.height # finds y value of bottom right
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))


    def apply(self, pos):
        # Convert world pos to camera/screen pos
        return pygame.Vector2(pos.x - self.x, pos.y - self.y)
    
    def undo(self, pos):
        #Convert screen pos to world pos
        return pygame.Vector2(pos.x + self.x, pos.y + self.y)

# Create camera
camera = Camera(
    int(WINDOW_WIDTH / ZOOM),
    int(WINDOW_HEIGHT / ZOOM),
    BG_WIDTH,
    BG_HEIGHT,
    zoom=ZOOM
)
# Create render surface after camera is created
render_surface = pygame.Surface((camera.width, camera.height))

# Fullscreen toggle state
fullscreen = False

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Fullscreen - Alex
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
            else:
                info = pygame.display.Info()
                WINDOW_WIDTH = info.current_w - 10
                WINDOW_HEIGHT = info.current_h - 10
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            camera.width = int(WINDOW_WIDTH / ZOOM)
            camera.height = int(WINDOW_HEIGHT / ZOOM)
            render_surface = pygame.Surface((camera.width, camera.height))

        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            camera.width = int(WINDOW_WIDTH / ZOOM)
            camera.height = int(WINDOW_HEIGHT / ZOOM)
            render_surface = pygame.Surface((camera.width, camera.height))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            projectile_rect = projectile_image.get_rect(center = player_pos)
            mouse_pos = pygame.mouse.get_pos()
            direction = pygame.Vector2(mouse_pos) - player_pos
            direction = direction.normalize() * 10 
            projectiles.append({"rect": projectile_rect, "velocity": direction})

    # Player movement - Riley
    keys = pygame.key.get_pressed() # Gets all the keys on the keyboard and returns true for the ones being pressed
    # Checks to see if any movement keys are being pressed and moves the player accordingly
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= player_vel
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += player_vel
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= player_vel
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += player_vel

    # Close the game if the player presses escape - Riley
    if keys[pygame.K_ESCAPE]:
        exit()

    # Clamp player position to background - Riley
    if player_pos.x <= 30: # If player goes too far left, stop them
        player_pos.x = 30

    if player_pos.x >= BG_WIDTH - 20: # If player goes too far right, stop them
        player_pos.x = BG_WIDTH - 20

    if player_pos.y <= 20: # If the player goes too far up, stop them
        player_pos.y = 20

    if player_pos.y >= 880: # If the player goes too far down, stop them
        player_pos.y = 880


    # update player rectangle position to player position - Alex
    player_rect.center = player_pos

    # Update camera to follow player - Alex
    camera.update(player_pos)

    # Draw everything to render_surface (world coordinates)
    render_surface.blit(background_img, (0, 0), area=pygame.Rect(camera.x, camera.y, camera.width, camera.height))


    # Draw NPC at camera-relative position
    npc_screen_pos = camera.apply(npc_pos)
    npc_draw_rect = npc_img.get_rect(center=npc_screen_pos)
    render_surface.blit(npc_img, npc_draw_rect)

    # NPC dialouge
    npc_dialouge = False

    # Draw player at camera-relative position
    player_screen_pos = camera.apply(player_pos)
    player_draw_rect = player.get_rect(center=player_screen_pos)
    render_surface.blit(player, player_draw_rect)

    # Scale render_surface to screen for zoom effect
    scaled_surface = pygame.transform.smoothscale(render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    for projectile in projectiles:
        projectile["rect"].centerx += projectile["velocity"].x
        projectile["rect"].centery += projectile["velocity"].y

        render_surface.blit(projectile_image, projectile_rect)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()
