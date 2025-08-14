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
background_img = pygame.image.load("background_full.png").convert_alpha()
BG_WIDTH, BG_HEIGHT = background_img.get_size()

#player - Riley
player = pygame.image.load('sprites/player.png').convert_alpha() # load the player image
player = pygame.transform.scale(player, (50, 50)) # set player size
player_pos = pygame.Vector2(100, 550) # set initial player position
player_rect = pygame.Rect(0, 0, 20, 20) # Player rectangle for collisions
player_rect.center = player_pos
player_vel = 400 # player speed (pixels per second)

# NPC - Alex
npc_img = pygame.image.load('sprites/NPC.png').convert_alpha()
npc_img = pygame.transform.scale(npc_img, (70, 70))
npc_pos = pygame.Vector2(1000, 850)
npc_rect = npc_img.get_rect(center=npc_pos)

# projectiles - Riley
projectile_image = pygame.image.load('sprites/player_projectile.png').convert_alpha()
projectile_image = pygame.transform.scale(projectile_image, (40, 40))
projectiles = []
projectile_vel = 700

# enemies - Riley
enemies = []
enemy_projectiles = []
enemy_image = pygame.image.load('sprites/enemy.png').convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (70, 70))
enemy_vel = 3

def create_enemy(pos_x, pos_y):
    enemy_rect = pygame.Rect(pos_x, pos_y, 70, 70)
    enemies.append({"rect": enemy_rect})

create_enemy(178, 222)

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

# Create camera
camera = Camera(
    int(WINDOW_WIDTH / ZOOM),
    int(WINDOW_HEIGHT / ZOOM),
    BG_WIDTH,
    BG_HEIGHT,
    zoom=ZOOM
)
# Create render surface after camera is created
render_surface = pygame.Surface(((camera.width, camera.height)), pygame.SRCALPHA)

# Fullscreen toggle state
fullscreen = False

# List of rectangles for collision - Riley
collision_rects = [
    pygame.Rect(670, 790, 247, 160),
    pygame.Rect(670, 575, 8, 215),
    pygame.Rect(915, 560, 2, 250),
    pygame.Rect(785, 728, 30, 4),
    pygame.Rect(777, 762, 53, 2),
    pygame.Rect(460, 680, 210, 2),
    pygame.Rect(915, 680, 470, 2),
    pygame.Rect(915, 545, 200, 2),
    pygame.Rect(670, 315, 500, 8),
    pygame.Rect(670, 315, 2, 130),
    pygame.Rect(1168, 315, 2, 132),
    pygame.Rect(980, 815, 45, 62),
    pygame.Rect(40, 1045, 640, 2),
    pygame.Rect(680, 1045, 2, 250),
    pygame.Rect(920, 1045, 970, 2),
    pygame.Rect(920, 1045, 2, 250),
    pygame.Rect(50, 200, 2, 845),
    pygame.Rect(50, 200, 1870, 2),
    pygame.Rect(1920, 200, 2, 750),
    pygame.Rect(680, 1295, 242, 2),
    pygame.Rect(1947, 965, 2, 120)
]

# function for making diagnal collision lines
def diagnal_line(length, start_x, start_y, x_step, y_step):
    for i in range(length):
        rect = pygame.Rect(start_x + i * x_step, start_y + i * y_step, 2, 2)
        collision_rects.append(rect)

def draw_tree_type1(x, y):
    diagnal_line(29, x, y, 1, 1.5)
    diagnal_line(31, x, y, -1, 1.5)
    diagnal_line(27, x + 30, y + 45, 1, 5)
    diagnal_line(28, x - 30, y + 45, -0.5, 5)
    collision_rects.append(pygame.Rect(x - 42, y + 180, 100, 2))
    collision_rects.append(pygame.Rect(x, y + 180, 2, 17))
    collision_rects.append(pygame.Rect(x + 29, y + 180, 2, 17))
    collision_rects.append(pygame.Rect(x, y + 197, 31, 2))

def draw_tree_type2(x, y):
    diagnal_line(33, x, y, 1, 1.6)
    diagnal_line(37, x, y, -1, 1.5)
    diagnal_line(42, x + 30, y + 45, 1, 3)
    diagnal_line(42, x - 30, y + 45, -1, 3)
    diagnal_line(50, x + 20, y + 200, 1, -0.5)
    diagnal_line(50, x - 20, y + 200, -1, -0.5)
    collision_rects.append(pygame.Rect(x - 20, y + 200, 2, 18))
    collision_rects.append(pygame.Rect(x + 20, y + 200, 2, 18))
    collision_rects.append(pygame.Rect(x - 20, y + 218, 40, 2))

draw_tree_type1(400, 570)
draw_tree_type1(127, 90)
draw_tree_type1(460, 120)
draw_tree_type1(1003, 570)
draw_tree_type1(1122, 600)
draw_tree_type1(1425, 85)
draw_tree_type1(1665, 720)
draw_tree_type1(1845, 150)

draw_tree_type2(1288, 790)
draw_tree_type2(1500, 760)
draw_tree_type2(1258, 545)
draw_tree_type2(565, 550)
draw_tree_type2(322, 34)
draw_tree_type2(1830, 790)
draw_tree_type2(1560, 153)
draw_tree_type2(1710, 65)

diagnal_line(10, 777, 762, 1, -3.5)
diagnal_line(17, 830, 762, -1, -2)
diagnal_line(53, 670, 575, -4, 2)
diagnal_line(135, 1115, 545, 2, 1)
diagnal_line(125, 1170, 450, 2, 1)
diagnal_line(110, 670, 450, -2, 1)
diagnal_line(50, 1920, 950, 1, 0.5)
diagnal_line(60, 1890, 1045, 1, 0.7)

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
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            mouse_pos.y -= 100
            mouse_pos.x -= 40
            player_screen_pos = camera.apply(player_pos)  # Get the player's position on screen
            direction = mouse_pos - player_screen_pos

            if direction.length() != 0:
                speed = projectile_vel
                direction = direction.normalize()
                velocity = direction * speed

            # Create projectile in world space using player's current world position
            projectile_rect = projectile_image.get_rect(center = player_pos)
            projectiles.append({"rect": projectile_rect, "velocity": velocity})

    # Player movement - Riley
    keys = pygame.key.get_pressed() # Gets all the keys on the keyboard and returns true for the ones being pressed
    dt = clock.tick(60) / 1000


    # Move vertically
    old_y = player_pos.y
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos.y -= player_vel * dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += player_vel * dt

    player_rect.center = player_pos  # Update rect position
    # If the player touches a collision rectangle vertically, stop them from moving further
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            player_pos.y = old_y
            player_rect.center = player_pos
            break

    # Move horizontally
    old_x = player_pos.x
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos.x -= player_vel * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += player_vel * dt

    player_rect.center = player_pos  # Update rect position
    # if the player touches a collision rectangle horizontally, stop them from moving further
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            player_pos.x = old_x
            player_rect.center = player_pos
            break

    # Close the game if the player presses escape - Riley
    if keys[pygame.K_ESCAPE]:
        exit()

    # update player rectangle position to player position - Riley
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

    # Draw the collision rectangles in a way that they do move with the camera, but stay fixed to the map
    for rect in collision_rects:
        cam_rect = rect.copy()
        cam_rect.topleft = camera.apply(pygame.Vector2(rect.topleft))
        pygame.draw.rect(render_surface, 'red', cam_rect, 2)

    to_remove = []
    moving = []
    deads = []
    for enemy in enemies:
        enemy_screen_pos = camera.apply(pygame.Vector2(enemy["rect"].topleft))
        render_surface.blit(enemy_image, enemy_screen_pos)

        enemy_pos = pygame.Vector2(enemy["rect"].center)
        enemy_direction = player_pos - enemy_pos
        distance = enemy_direction.length()

        if distance > 1 and distance < 300:
            if distance > 1:
                enemy_direction = enemy_direction.normalize() * enemy_vel

            enemy["rect"].x += enemy_direction.x
            enemy["rect"].y += enemy_direction.y

            player_screen_pos = camera.apply(player_pos)
            proj_directionx = player_screen_pos.x - enemy["rect"].x
            proj_directiony = player_screen_pos.y - enemy["rect"].y
            proj_direction = pygame.Vector2(proj_directionx, proj_directiony)

            if proj_direction.length() != 0:
                proj_direction = proj_direction.normalize() * projectile_vel

            enemy_projectile_rect = projectile_image.get_rect(center = enemy["rect"].center)
            enemy_projectiles.append({"rect": enemy_projectile_rect, "direction": proj_direction})

        for proj in projectiles:
            if proj["rect"].colliderect(enemy["rect"]):
                deads.append(enemy)

                if proj in projectiles:
                    projectiles.remove(proj)

        for dead in deads:
            if dead in enemies:
                enemies.remove(dead)

    for proj in projectiles:
        proj["rect"].centerx += proj["velocity"].x * dt
        proj["rect"].centery += proj["velocity"].y * dt

        cam_rect = proj["rect"].copy()
        cam_rect.topleft = camera.apply(pygame.Vector2(proj["rect"].topleft))
        render_surface.blit(projectile_image, cam_rect.topleft)

        for rect in collision_rects:
            if rect.colliderect(proj["rect"]):
                to_remove.append(proj)
                break

        for proj in to_remove:
            if proj in projectiles:
                projectiles.remove(proj)


    # Scale render_surface to screen for zoom effect
    scaled_surface = pygame.transform.smoothscale(render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    print(pygame.mouse.get_pos())

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()
