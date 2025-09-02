import pygame
import sys
import os
import pickle as p

# Start pygame
pygame.init()

# Window Settings
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w - 10
WINDOW_HEIGHT = info.current_h - 10
FPS = 60
start_colour = (10 , 10 , 30)
end_colour = (80, 80, 120)

# Load sounds
trumpet = pygame.mixer.Sound("start_game_effect.mp3") # Trumpet sound for starting the game
trumpet.set_volume(0.3)
water_drip = pygame.mixer.Sound("water_drip.mp3")
insane_guitar = pygame.mixer.Sound("insane_guitar.mp3")

ZOOM = 1.2  # zoom level 

# Camera dead zone - Alex
CAMERA_MARGIN_X = 120
CAMERA_MARGIN_Y = 80

# Game Menu 
game_state = "menu"
game_over_time = 0

# Timer variables
game_start_time = 0
timer_font = pygame.font.Font(None, 36)
timer_border_location = 10
timer_location = 15

# Lighting variables
lighting_enabled = True
light_sources = []
darkness_colour = (20,20,40)

def create_menu_background(w, h):
    surf = pygame.Surface((w, h))  
    for y in range(h):
        t = y / h
        colour_value = (
            int(start_colour[0] + (end_colour[0] - start_colour[0]) * t),
            int(start_colour[1] + (end_colour[1] - start_colour[1]) * t),
            int(start_colour[2] + (end_colour[2] - start_colour[2]) * t)
        )
        pygame.draw.line(surf, colour_value, (0, y), (w, y))
    return surf

menu_background = None
menu_bg_size = (0, 0)

def get_menu_background():
    global menu_background, menu_bg_size
    current_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    
    if menu_background is None or menu_bg_size != current_size:
        menu_background = create_menu_background(WINDOW_WIDTH, WINDOW_HEIGHT)
        menu_bg_size = current_size
    
    return menu_background

def draw_menu(): 
    screen.blit(get_menu_background(), (0, 0))

    # Game title
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render("Dark to Light", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
    title_center_pos = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT // 2)
  
    # Draw shadow first
    shadow_title = title_font.render("Dark to Light", True, (50, 50, 50))
    screen.blit(shadow_title, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title_text, title_rect)
    
    # Play button
    button_font = pygame.font.Font(None, 60)
    button_text = button_font.render("Play", True, (255, 255, 255))
    
    # Button rectangle
    button_width = 200
    button_height = 80
    button_x = (WINDOW_WIDTH - button_width) // 2
    button_y = WINDOW_HEIGHT // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Check if mouse is hovering over button
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = button_rect.collidepoint(mouse_pos)
    
    # Draw button with hover effect
    button_color = (70, 130, 180) if is_hovering else (40, 80, 140)
    border_color = (100, 150, 200) if is_hovering else (80, 80, 120)
    
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, border_color, button_rect, 3)
    
    # Center the text on the button
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    # Instructions
    instruction_font = pygame.font.Font(None, 30)
    instruction_text = instruction_font.render("Click Play to start your adventure!", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 250))
    screen.blit(instruction_text, instruction_rect)
    
    return button_rect

def game_over():
    game_over_font = pygame.font.Font(None, 80)
    game_over_txt = game_over_font.render('Game Over', True, 'white')
    game_over_rect = game_over_txt.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    screen.blit(bg, (0, 0))
    screen.blit(game_over_txt, game_over_rect)
    pygame.init()

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
pygame.display.set_caption("Dark to Light")
clock = pygame.time.Clock()

# Load background image - Alex
background_img = pygame.image.load("background_full.png").convert_alpha()
BG_WIDTH, BG_HEIGHT = background_img.get_size()

#player - Riley
player = pygame.image.load('sprites/player.png').convert_alpha() # load the player image
player = pygame.transform.scale(player, (50, 50)) # set player size
player_pos = pygame.Vector2(1150, 950) # set initial player position
player_rect = pygame.Rect(0, 0, 20, 20) # Player rectangle for collisions
player_rect.center = player_pos
player_vel = 150 # player speed

# Load heart icon
heart_img = pygame.image.load("heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30,30))

# Player lives - Alex
player_lives = 3
health_font = pygame.font.Font(None, 36)

# NPC - Alex
npc_img = pygame.image.load('sprites/NPC.png').convert_alpha()
npc_img = pygame.transform.scale(npc_img, (70, 70))
npc_pos = pygame.Vector2(1000, 850)
npc_rect = npc_img.get_rect(center=npc_pos)

# projectiles - Riley
projectile_image = pygame.image.load('sprites/player_projectile.png').convert_alpha() # saves the projectile image
projectile_image = pygame.transform.scale(projectile_image, (30, 30))
projectiles = [] # create a list to store information for projectiles (eg position)
projectile_vel = 130 # set the speed of the projectile

enemy_projectiles = []
enemy_proj_image = pygame.image.load('sprites/enemy_projectile.png').convert_alpha()
enemy_proj_image = pygame.transform.scale(enemy_proj_image, (30, 30))
enemy_proj_vel = 400

portal_img = pygame.image.load('sprites/portal.png')
portal_img = pygame.transform.scale(portal_img, (120, 120))
portal_rect = pygame.Rect(730, 1100, 150, 150)

enemies = []
enemy_image = pygame.image.load('sprites/enemy.png').convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (60, 60))
enemy_vel = 100
enemy_positions = [
    pygame.Vector2(950, 1000),
    pygame.Vector2(1140, 700),
    pygame.Vector2(700, 1100),
    pygame.Vector2(800, 1100),
    pygame.Vector2(700, 650),
    pygame.Vector2(850, 650)
]

interacted_with_npc = False
level_1_spawned = False

def create_enemy(pos):
    enemy_rect = pygame.Rect(pos.x, pos.y, 40, 40)
    enemies.append({
        "rect": enemy_rect,
        "last_shot": 0,
        "cooldown": 1000
    })

def reset_enemies():
    enemies.clear()
    if interacted_with_npc:
        for pos in enemy_positions:
            create_enemy(pos)
    
def create_enemies():
    for pos in enemy_positions:
        create_enemy(pos)

def level_1():
    create_enemies()

lvl2_background_img = pygame.image.load('background.png')
in_level_2 = False

def level_2():
    global in_level_2, render_surface, darkness_surface
    in_level_2 = True
    render_surface, darkness_surface = get_render_surfaces()
    render_surface.blit(lvl2_background_img, (0, 0))


hearts = []
def create_heart(pos):
    heart_rect = pygame.Rect(pos.x, pos.y, 20, 20)
    hearts.append({"rect": heart_rect})

def spawn_hearts():
    heart_positions = [
        pygame.Vector2(750, 1250),
        pygame.Vector2(780, 650)    
    ]
    for pos in heart_positions:
        create_heart(pos)

spawn_hearts()

# NPC Dialogue
dialogue_font = pygame.font.Font(None, 24)  # Font for dialogue text
dialogue_active = False  # Is dialogue currently being shown?
dialogue_index = 0  # Which line of dialogue are we on?
interaction_distance = 100  # How close the player needs to be to interact

# Placeholder dialogue for the NPC in a dictionary
npc_dialogue = [
    {"speaker": "NPC", "text": "Hello there, traveler! Welcome to our village."}, # Format: "speaker", "text" 
    {"speaker": "NPC", "text": "The journey ahead is dangerous. You'll need to be prepared."},
    {"speaker": "NPC", "text": "Take this advice: always watch your back in the dark forest."},
    {"speaker": "Player", "text": "Thank you for the warning. I'll be careful."},
    {"speaker": "NPC", "text": "Good luck on your adventure!"}
]

# Dialogue box settings
dialogue_box_width = 600
dialogue_box_height = 150
dialogue_padding = 20
dialogue_text_color = (255, 255, 255) # White text colour
dialogue_box_color = (50, 50, 50) # Dark black box colour
dialogue_border_color = (200, 200, 200) # Grey for border
speaker_color = (255, 215, 0)  # Gold for speaker

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
    pygame.Rect(1947, 965, 2, 120),
    pygame.Rect(813, 1148, 17, 45),
    pygame.Rect(755, 1148, 20, 45),
    pygame.Rect(755, 1160, 60, 2)
]


def create_boundary_walls():
    """Create collision rectangles for the outer boundaries of the background"""
    boundary_rects = []
    wall_thickness = 50  # Make walls thick enough so player can't slip through
    
    # Top wall (positioned above the background)
    boundary_rects.append(pygame.Rect(0, -wall_thickness, BG_WIDTH, wall_thickness))
    # Bottom wall (positioned below the background)
    boundary_rects.append(pygame.Rect(0, BG_HEIGHT, BG_WIDTH, wall_thickness))
    # Left wall (positioned to the left of the background)
    boundary_rects.append(pygame.Rect(-wall_thickness, 0, wall_thickness, BG_HEIGHT))
    # Right wall (positioned to the right of the background)
    boundary_rects.append(pygame.Rect(BG_WIDTH, 0, wall_thickness, BG_HEIGHT))
    
    return boundary_rects

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
diagnal_line(20, 790, 1105, 1.5, 1)
diagnal_line(20, 790, 1105, -1.5, 1)
diagnal_line(10, 820, 1125, 1, 2.3)
diagnal_line(7, 760, 1125, -1, 4)
diagnal_line(15, 830, 1193, 1, 1)
diagnal_line(15, 755, 1193, -1, 1)

# Create boundary walls and add them to collision_rects
boundary_walls = create_boundary_walls()
collision_rects.extend(boundary_walls)

# Create camera
camera = Camera(
    int(WINDOW_WIDTH / ZOOM),
    int(WINDOW_HEIGHT / ZOOM),
    BG_WIDTH,
    BG_HEIGHT,
    zoom=ZOOM
)

render_surface = None
darkness_surface = None
current_camera_size = (0, 0)

def get_render_surfaces():
    global render_surface, darkness_surface, current_camera_size
    camera_size = (camera.width, camera.height)
    
    # Only recreate if camera size changed
    if render_surface is None or current_camera_size != camera_size:
        render_surface = pygame.Surface(camera_size, pygame.SRCALPHA)
        darkness_surface = pygame.Surface(camera_size)
        current_camera_size = camera_size
    
    return render_surface, darkness_surface

# Fullscreen toggle state
fullscreen = False

# Function to wrap text for dialogue box
def wrap_text(text, font, max_width):
    """Break text into lines that fit within max_width"""
    words = text.split(' ') # Input text is split into individual words
    lines = [] # Blank lines list
    current_line = [] # Blank current lines list
     
    for word in words: # For every word that is in the list "words"
        test_line = ' '.join(current_line + [word]) # Adds the word to the current line
        text_width = font.size(test_line)[0] # Measures the pixel width of the test_line ## Makes it so that it can dynamically change according to the font size
        
        if text_width <= max_width: # if the word is added and it is within the max_width limit
            current_line.append(word) # Add the word to the line
        else:
            if current_line:
                lines.append(' '.join(current_line)) # Adds the current_line to the lines list
                current_line = [word] # Current word starts a new line
            else: 
                lines.append(word) # If current line is empty, then add word to a new line
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

# Function to draw dialogue box
def draw_dialogue_box(surface, speaker, text):
    """Draw the dialogue box with speaker name and text"""
    # Calculate dialogue box position (bottom center of screen)
    box_x = (surface.get_width() - dialogue_box_width) // 2
    box_y = surface.get_height() - dialogue_box_height - 50
    
    # Draw dialogue box background
    pygame.draw.rect(surface, dialogue_box_color, 
                     (box_x, box_y, dialogue_box_width, dialogue_box_height))
    pygame.draw.rect(surface, dialogue_border_color, 
                     (box_x, box_y, dialogue_box_width, dialogue_box_height), 3)
    
    # Draw speaker name
    speaker_surface = dialogue_font.render(f"{speaker}:", True, speaker_color)
    surface.blit(speaker_surface, (box_x + dialogue_padding, box_y + dialogue_padding))
    
    # Draw dialogue text (with word wrapping)
    text_lines = wrap_text(text, dialogue_font, dialogue_box_width - 2 * dialogue_padding)
    y_offset = dialogue_padding + 30  # Start below speaker name
    
    for line in text_lines: # For each line of wrapped text
        text_surface = dialogue_font.render(line, True, dialogue_text_color) # Renders the current line
        surface.blit(text_surface, (box_x + dialogue_padding, box_y + y_offset))
        y_offset += 25
    
    # Draw continue indicator
    indicator_text = "Click to continue..." if dialogue_index < len(npc_dialogue) - 1 else "Click to close" # Detects if its the last line. If not, then display "Click to continue...", if it is display "Click to close"
    indicator_surface = dialogue_font.render(indicator_text, True, (150, 150, 150))
    indicator_x = box_x + dialogue_box_width - indicator_surface.get_width() - dialogue_padding
    indicator_y = box_y + dialogue_box_height - 30
    surface.blit(indicator_surface, (indicator_x, indicator_y))

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Menu interactions
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Get the play button rect from draw_menu
                play_button = draw_menu()  # This will be called again below, but we need the rect
                mouse_pos = pygame.mouse.get_pos()
                if play_button.collidepoint(mouse_pos):
                    game_state = "playing"
                    player_lives = 3
                    interacted_with_npc = False
                    level_1_spawned = False
                    reset_enemies()
                    player_pos = pygame.Vector2(1150, 950)
                    player_rect.center = player_pos
                    trumpet.play()
                    game_start_time = pygame.time.get_ticks()  # Record when game started

        # Game interactions (only when playing)
        elif game_state == "playing":
            # Fullscreen - Alex
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
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

            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                camera.width = int(WINDOW_WIDTH / ZOOM)
                camera.height = int(WINDOW_HEIGHT / ZOOM)

            # Handle dialogue interaction
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if not dialogue_active and not interacted_with_npc:
                    # Check if player is close enough to NPC
                    distance = player_pos.distance_to(npc_pos)
                    if distance <= interaction_distance:
                        dialogue_active = True
                        dialogue_index = 0

            # Handle mouse clicks for dialogue progression
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dialogue_active:
                    # Check if click is on dialogue box
                    box_x = (WINDOW_WIDTH - dialogue_box_width) // 2
                    box_y = WINDOW_HEIGHT - dialogue_box_height - 50
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    if (box_x <= mouse_x <= box_x + dialogue_box_width and 
                        box_y <= mouse_y <= box_y + dialogue_box_height):
                        dialogue_index += 1
                        if dialogue_index >= len(npc_dialogue):
                            dialogue_active = False
                            dialogue_index = 0
                            interacted_with_npc = True
                                
                else:
                    # Original projectile code
                    projectile_rect = projectile_image.get_rect(center = player_pos)
                    mouse_pos = pygame.mouse.get_pos()
                    # Convert mouse position to world coordinates considering zoom
                    mouse_world_x = (mouse_pos[0] / ZOOM) + camera.x
                    mouse_world_y = (mouse_pos[1] / ZOOM) + camera.y
                    mouse_world_pos = pygame.Vector2(mouse_world_x, mouse_world_y)
                    
                    direction = mouse_world_pos - player_pos
                    if direction.length() > 0:
                        direction = direction.normalize() * projectile_vel * dt
                        projectiles.append({"rect": projectile_rect, "velocity": direction})

    # Handle different game states
    if game_state == "menu":
        # Draw the menu
        draw_menu()

    elif game_state == "game_over":
        game_over()

        if pygame.time.get_ticks() - game_over_time > 2000:
            game_state = "menu"
            game_over_time = 0
        
    elif game_state == "playing":
        keys = pygame.key.get_pressed()

        # Move vertically
        old_y = player_pos.y
        if not dialogue_active:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_pos.y -= player_vel * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_pos.y += player_vel * dt

        player_rect.center = player_pos  # Update rect position
        
        # Simple collision detection for vertical movement (no optimization)
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                if rect == pygame.Rect(755, 1160, 60, 2) and not in_level_2:
                    if len(enemies) == 0 and interacted_with_npc:
                        level_2()

                player_pos.y = old_y
                player_rect.center = player_pos
                break

        # Move horizontally
        old_x = player_pos.x
        if not dialogue_active:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_pos.x -= player_vel * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_pos.x += player_vel * dt

        player_rect.center = player_pos  # Update rect position
        
        # Simple collision detection for horizontal movement (no optimization)
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                if rect == pygame.Rect(755, 1160, 60, 2):
                    level_2()

                player_pos.x = old_x
                player_rect.center = player_pos
                break

        # Close the game if the player presses escape - Riley
        if keys[pygame.K_ESCAPE]:
            exit() # Return to menu instead of exiting

        # update player rectangle position to player position - Riley
        player_rect.center = player_pos

        # Update camera to follow player - Alex
        camera.update(player_pos)

        render_surface, darkness_surface = get_render_surfaces()

        # Draw everything to render_surface (world coordinates)
        if in_level_2:
            render_surface.blit(lvl2_background_img, (0, 0), area=pygame.Rect(camera.x, camera.y, camera.width, camera.height))

        else:
            render_surface.blit(background_img, (0, 0), area=pygame.Rect(camera.x, camera.y, camera.width, camera.height))

        # Draw NPC at camera-relative position
        npc_screen_pos = camera.apply(npc_pos)
        npc_draw_rect = npc_img.get_rect(center=npc_screen_pos)
        render_surface.blit(npc_img, npc_draw_rect)

        # Draw interaction prompt if player is close to NPC (and not in dialogue)
        if not dialogue_active and not interacted_with_npc:
            distance = player_pos.distance_to(npc_pos)
            if distance <= interaction_distance:
                prompt_text = dialogue_font.render("Press E to talk", True, (255, 255, 255))
                prompt_pos = (npc_screen_pos.x - prompt_text.get_width() // 2, 
                             npc_screen_pos.y - 50)
                render_surface.blit(prompt_text, prompt_pos)

        portal_rect2 = portal_rect.copy()
        portal_rect2.topleft = camera.apply(pygame.Vector2(portal_rect2.topleft))
        render_surface.blit(portal_img, portal_rect2.topleft)

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

                enemy["rect"].x += enemy_direction.x * dt
                enemy["rect"].y += enemy_direction.y * dt

                player_screen_pos = camera.apply(player_pos)
                proj_directionx = player_screen_pos.x - enemy["rect"].x
                proj_directiony = player_screen_pos.y - enemy["rect"].y
                proj_direction = pygame.Vector2(proj_directionx, proj_directiony)

                if proj_direction.length() != 0:
                    proj_direction = proj_direction.normalize() * projectile_vel

                # enemy projectiles
                current_time = pygame.time.get_ticks()

                if current_time - enemy.get("last_shot", 0) > enemy["cooldown"]:
                    enemy_pos = pygame.Vector2(enemy["rect"].center)
                    enemy_proj_direction = player_pos - enemy_pos

                    if enemy_proj_direction.length() > 0:
                        enemy_proj_direction = enemy_proj_direction.normalize() * enemy_proj_vel
                        enemy_proj_rect = enemy_proj_image.get_rect(center = enemy_pos)
                        enemy_projectiles.append({"rect": enemy_proj_rect, "velocity": enemy_proj_direction})
                        enemy["last_shot"] = current_time

                enemy_moving = True
                for rect in collision_rects:
                    if enemy["rect"].colliderect(rect):
                        enemy_moving = False

                if not enemy_moving:
                    enemy_vel = 0

                elif enemy_moving:
                    enemy_vel = 100

            for proj in projectiles:
                if proj["rect"].colliderect(enemy["rect"]):
                    deads.append(enemy)

                    if proj in projectiles:
                        projectiles.remove(proj)

            for dead in deads:
                if dead in enemies:
                    enemies.remove(dead)

        for proj in enemy_projectiles:
            proj["rect"].centerx += proj["velocity"].x * dt
            proj["rect"].centery += proj["velocity"].y * dt

            cam_rect = proj["rect"].copy()
            cam_rect.topleft = camera.apply(pygame.Vector2(proj["rect"].topleft))
            render_surface.blit(enemy_proj_image, cam_rect.topleft)

            if player_rect.colliderect(proj["rect"]):
                player_lives -= 1
                
                if proj in enemy_projectiles:
                    to_remove.append(proj)

            for rect in collision_rects:
                if rect.colliderect(proj["rect"]):
                    to_remove.append(proj)
                    break

            for proj in to_remove:
                if proj in enemy_projectiles:
                    enemy_projectiles.remove(proj)

        for proj in projectiles:
            proj["rect"].centerx += proj["velocity"].x * projectile_vel * dt
            proj["rect"].centery += proj["velocity"].y * projectile_vel * dt

            proj_rect = proj["rect"].copy()
            proj_rect.topleft = camera.apply(pygame.Vector2(proj["rect"].topleft))
            render_surface.blit(projectile_image, proj_rect.topleft)

            for rect in collision_rects:
                if rect.colliderect(proj["rect"]):
                    to_remove.append(proj)
                    break

            for proj in to_remove:
                if proj in projectiles:
                    projectiles.remove(proj)


        if player_lives == 0:
            game_state = "game_over"
            game_over_time = pygame.time.get_ticks()

        if interacted_with_npc:
            if not level_1_spawned:
                insane_guitar.play()
                level_1()
                level_1_spawned = True

        hearts_to_remove = []
        if player_lives < 3:
            for heart in hearts:
                heart_rect = heart["rect"].copy()
                heart_rect.topleft = camera.apply(pygame.Vector2(heart["rect"].topleft))
                render_surface.blit(heart_img, heart_rect.topleft)

                if player_rect.colliderect(heart["rect"]):
                    player_lives += 1
                    hearts_to_remove.append(heart)

            for heart in hearts_to_remove:
                if heart in hearts:
                    hearts.remove(heart)


        # OPTIMIZATION 3: Improved lighting with fewer circles
        if lighting_enabled:
            # Fill the game with darkness
            darkness_surface.fill(darkness_colour)

            light_center = (int(player_screen_pos.x), int(player_screen_pos.y))
            max_radius = 250  # The outermost edge of the light
            step = 6  # OPTIMIZED: Increased from 2 to 6 (fewer circles = better performance)

            for radius in range(max_radius, 0, -step): # Much fewer iterations now
                # Calculate brightness for the current ring
                light_intensity = 3
                normalized_radius = radius / max_radius
                brightness = int(light_intensity * 255 * (1 - normalized_radius**1.2))

                # Ensure brightness stays within the valid range of 0 and 255
                brightness = max(0, min(255, brightness))

                # RGB of the light
                light_color = (brightness, brightness, brightness)
                
                # Draw the circle for this ring of light onto our light map.
                pygame.draw.circle(darkness_surface, light_color, light_center, radius)

                #if len(enemies) == 0 and interacted_with_npc:
                temp_rect = pygame.Rect(0, 0, 0, 0)
                temp_rect.center = (portal_rect.centerx - 13, portal_rect.centery - 10)
                portal_center_screen = camera.apply(temp_rect)

                if len(enemies) == 0 and interacted_with_npc:
                    pygame.draw.circle(darkness_surface, light_color, portal_center_screen, 90)



            render_surface.blit(darkness_surface, (0,0), special_flags=pygame.BLEND_MULT)

        # Scale render_surface to screen for zoom effect
        scaled_surface = pygame.transform.smoothscale(render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        # Draw dialogue box on top of everything (if active)
        if dialogue_active:
            current_dialogue = npc_dialogue[dialogue_index]
            draw_dialogue_box(screen, current_dialogue["speaker"], current_dialogue["text"])
        
        # Draw timer on top left (always visible during gameplay)
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - game_start_time) // 1000
        timer_text = timer_font.render(f"Timer: {elapsed_seconds}s", True, (255, 255, 255))
        
        # semi-transparent background for better readability
        timer_bg = pygame.Surface((timer_text.get_width() + 20, timer_text.get_height() + 10))
        timer_bg.fill((0, 0, 0))
        timer_bg.set_alpha(128)  # Semi-transparent
        
        screen.blit(timer_bg, (10, timer_border_location))
        screen.blit(timer_text, (20, timer_location))

       # Draw hearts on top left below timer
        heart_y = timer_location + 40
        for i in range(player_lives):
            heart_x = 20 + (i * 35)  # 35 = heart width + spacing
            screen.blit(heart_img, (heart_x, heart_y))

    # Update display
    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()

