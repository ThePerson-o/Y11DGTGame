import pygame
import sys
import os
import pickle as p
from googletrans import Translator


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
soundtrack_1 = pygame.mixer.Sound("soundtrack 1.mp3")
soundtrack_2 = pygame.mixer.Sound("soundtrack 2.mp3")
soundtrack_1.set_volume(0.2)
soundtrack_2.set_volume(0.2)

language = "en"
ZOOM = 1.2  # zoom level 

# Camera dead zone - Alex
CAMERA_MARGIN_X = 120
CAMERA_MARGIN_Y = 80

# Game Menu 
game_state = "menu"
selected_level = None  # Store the selected level

# Timer variables
game_start_time = 0
end_time = 0
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
    if language == "en":
        title_text = title_font.render("Dark to Light", True, (255, 255, 255))
    elif language == "mi":
        title_text = title_font.render("whēuriuri ko tūrama", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
    title_center_pos = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT // 2)
  
    # Draw shadow first
    if language == "en":
        shadow_title = title_font.render("Dark to Light", True, (50, 50, 50))
    elif language == "mi":
        shadow_title = title_font.render("whēuriuri ko tūrama", True, (50, 50, 50))
    screen.blit(shadow_title, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title_text, title_rect)
    
    # Play button
    button_font = pygame.font.Font(None, 60)
    if language == "en":
        button_text = button_font.render("Play", True, (255, 255, 255))
    elif language == "mi":
        button_text = button_font.render("Kori", True, (255, 255, 255))
    # Button rectangle
    button_width = 200
    button_height = 80
    button_x = (WINDOW_WIDTH - button_width) // 2
    button_y = WINDOW_HEIGHT // 2
    play_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    is_hovering_play = play_button_rect.collidepoint(mouse_pos)
    button_color_play = (70, 130, 180) if is_hovering_play else (40, 80, 140)
    border_color_play = (100, 150, 200) if is_hovering_play else (80, 80, 120)
    pygame.draw.rect(screen, button_color_play, play_button_rect)
    pygame.draw.rect(screen, border_color_play, play_button_rect, 3)
    text_rect = button_text.get_rect(center=play_button_rect.center)
    screen.blit(button_text, text_rect)

    # Settings button below Play button
    if language == "mi":
        settings_button_width = 350  
        settings_button_x = button_x - 60  
    else:
        settings_button_width = 250
        settings_button_x = button_x - 25
    settings_button_height = 80
    settings_button_y = button_y + button_height + 30  # 30px below Play button
    settings_button_rect = pygame.Rect(settings_button_x, settings_button_y, settings_button_width, settings_button_height)
    is_hovering_settings = settings_button_rect.collidepoint(mouse_pos)
    button_color_settings = (70, 130, 180) if is_hovering_settings else (40, 80, 140)
    border_color_settings = (100, 150, 200) if is_hovering_settings else (80, 80, 120)
    pygame.draw.rect(screen, button_color_settings, settings_button_rect)
    pygame.draw.rect(screen, border_color_settings, settings_button_rect, 3)
    
    # Settings icon (left side of button)
    settings_icon = pygame.image.load("setting.png")
    icon_width, icon_height = settings_icon.get_size()
    shrunk_size = (int(icon_width * 0.1), int(icon_height * 0.1))
    settings_icon = pygame.transform.smoothscale(settings_icon, shrunk_size)
    icon_rect = settings_icon.get_rect()
    icon_rect.centery = settings_button_rect.centery
    icon_rect.left = settings_button_rect.left + 10
    screen.blit(settings_icon, icon_rect)

    # Settings text (right of icon, centered vertically)
    if language == "en":
        settings_text = button_font.render("Settings", True, (255, 255, 255))
    elif language == "mi":
        settings_text = button_font.render("Kōwhiringa", True, (255, 255, 255))
    settings_text_rect = settings_text.get_rect()
    settings_text_rect.centery = settings_button_rect.centery 
    settings_text_rect.left = icon_rect.right + 10
    screen.blit(settings_text, settings_text_rect)
    # Instructions
    instruction_font = pygame.font.Font(None, 30)
    if language == "en":
        instruction_text = instruction_font.render("Click Play to start your adventure!", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 250))
    elif language == "mi":
        instruction_text = instruction_font.render("Pāwhiritia te Tākaro hei tīmata i tō mōrearea!", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 250))
    screen.blit(instruction_text, instruction_rect)
    
    return play_button_rect, settings_button_rect

# This is a function that draws a black screen with a message in the center of the screen to the player for completing the game.
def end_screen():
    seconds = (end_time - game_start_time) // 1000
    
    end_screen_font = pygame.font.Font(None, 40)
    end_screen_txt = end_screen_font.render(f'Congrats! You finished the game. Finish time: {seconds}. Press esc to exit.', True, 'white')
    end_screen_rect = end_screen_txt.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    screen.blit(bg, (0, 0))
    screen.blit(end_screen_txt, end_screen_rect)

game_finished = False
# function that draws a black screen with game over text in the center
def game_over():
    game_over_font = pygame.font.Font(None, 80)
    game_over_txt = game_over_font.render('Game Over', True, 'white')
    game_over_rect = game_over_txt.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    screen.blit(bg, (0, 0))
    screen.blit(game_over_txt, game_over_rect)
    pygame.init()


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
player_rect.center = player_pos # Move the player retangle onto the player position
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
projectile_image = pygame.transform.scale(projectile_image, (30, 30)) # Set projectile size
projectiles = [] # create a list to store information for projectiles (eg position)
projectile_vel = 60 # set the speed of the projectile

enemy_projectiles = [] # list to store information about enemy projectiles (eg posision)
enemy_proj_image = pygame.image.load('sprites/enemy_projectile.png').convert_alpha() # Load enemy projectile image
enemy_proj_image = pygame.transform.scale(enemy_proj_image, (30, 30)) # Set enemy projectile size
enemy_proj_vel = 400 # Enemy projectile speed

portal_img = pygame.image.load('sprites/portal.png') # Load portal image
portal_img = pygame.transform.scale(portal_img, (120, 120)) # Set portal size

enemies = [] # List to store enemies
enemy_image = pygame.image.load('sprites/enemy.png').convert_alpha() # load enemy image
enemy_image = pygame.transform.scale(enemy_image, (60, 60)) # set enemy image size
enemy_vel = 100 # enemy speed
# positions for enemies to be spawned
enemy_positions = [
    pygame.Vector2(745, 1255),
    pygame.Vector2(100, 300),
    pygame.Vector2(750, 650),
    pygame.Vector2(1000, 200),
    pygame.Vector2(1500, 600)
]

interacted_with_npc = False # Variable to check if the player has talked to NPC
level_1_spawned = False # Variable to check if level 1 has been spawned yet

objective = 'Talk to NPC'
objective_font = pygame.font.Font(None, 30)

# This function creates an enemy in the enemies list and stores important information about the enemy so it can be drawn on screen later
def create_enemy(pos):
    enemy_rect = pygame.Rect(pos.x, pos.y, 40, 40)
    enemies.append({
        "rect": enemy_rect,
        "last_shot": 0,
        "cooldown": 1000
    })

# This funtion clears the enemies list so that enemies are removed from the screen, and if the player has interacted with the npc, redraws them at their original positions.
def reset_enemies():
    enemies.clear()
    if interacted_with_npc:
        for pos in enemy_positions:
            create_enemy(pos)

# This function calls the create_enemy() funtion for every position in the enemy positions list
def create_enemies():
    for pos in enemy_positions:
        create_enemy(pos)

# This function calls the create_enemies() function
def level_1():
    create_enemies()

in_level_2 = False # Variable to check if the player is in level 2

# This function contains all the code for level 2 such as the new collisions and new player position.
def level_2():
    global in_level_2, collision_rects, enemy_positions, player_pos, objective
    in_level_2 = True
    # Set Level 2 objective (displayed as the yellow objective text)
    if language == "en":
        objective = 'Objective: Reach the End'
    elif language == "mi":
        objective = 'whāinga poto: Tae atu ki te mutunga'

    player_pos = pygame.Vector2(1000, 1200)

    collision_rects = [
        pygame.Rect(805, 790, 390, 60),
        pygame.Rect(805, 850, 53, 170),
        pygame.Rect(690, 960, 120, 60),
        pygame.Rect(690, 960, 60, 165),
        pygame.Rect(750, 1070, 215, 55),
        pygame.Rect(910, 900, 55, 180),
        pygame.Rect(910, 900, 180, 50),
        pygame.Rect(1140, 850, 55, 120),
        pygame.Rect(1140, 915, 170, 55),
        pygame.Rect(1255, 970, 55, 100),
        pygame.Rect(1140, 1020, 170, 57),
        pygame.Rect(1310, 1025, 215, 52),
        pygame.Rect(1025, 1000, 55, 230),
        pygame.Rect(1080, 1130, 557, 55),
        pygame.Rect(355, 1180, 610, 50),
        pygame.Rect(578, 860, 168, 55),
        pygame.Rect(578, 915, 55, 210),
        pygame.Rect(470, 1070, 110, 55),
        pygame.Rect(690, 690, 55, 170),
        pygame.Rect(745, 690, 180, 55),
        pygame.Rect(870, 585, 55, 110),
        pygame.Rect(925, 585, 172, 55),
        pygame.Rect(1042, 585, 55, 155),
        pygame.Rect(1042, 690, 260, 55),
        pygame.Rect(1247, 690, 55, 175),
        pygame.Rect(1247, 810, 170, 55),
        pygame.Rect(1362, 810, 55, 170),
        pygame.Rect(1470, 485, 55, 570),
        pygame.Rect(470, 490, 55, 530),
        pygame.Rect(575, 585, 55, 225),
        pygame.Rect(520, 755, 60, 55),
        pygame.Rect(575, 585, 240, 55),
        pygame.Rect(760, 380, 55, 205),
        pygame.Rect(760, 380, 222, 55),
        pygame.Rect(927, 380, 55, 155),
        pygame.Rect(927, 490, 275, 45),
        pygame.Rect(1147, 490, 55, 150),
        pygame.Rect(1147, 585, 265, 55),
        pygame.Rect(1357, 585, 55, 170),
        pygame.Rect(470, 175, 55, 255),
        pygame.Rect(470, 375, 125, 55),
        pygame.Rect(540, 375, 55, 160),
        pygame.Rect(540, 480, 165, 55),
        pygame.Rect(355, 75, 55, 530),
        pygame.Rect(355, 550, 115, 55),
        pygame.Rect(355, 660, 55, 520),
        pygame.Rect(470, 175, 420, 55),
        pygame.Rect(835, 175, 55, 160),
        pygame.Rect(835, 280, 255, 55),
        pygame.Rect(1035, 280, 55, 160),
        pygame.Rect(1035, 385, 270, 55),
        pygame.Rect(1250, 385, 55, 155),
        pygame.Rect(1250, 485, 220, 55),
        pygame.Rect(650, 175, 55, 350),
        pygame.Rect(355, 75, 1280, 55),
        pygame.Rect(1580, 75, 55, 1100),
        pygame.Rect(950, 130, 55, 100),
        pygame.Rect(950, 175, 250, 55),
        pygame.Rect(1145, 175, 55, 160),
        pygame.Rect(1145, 280, 270, 55),
        pygame.Rect(1360, 280, 55, 155),
        pygame.Rect(1360, 380, 220, 55),
        pygame.Rect(960, 1228, 100, 2),
        pygame.Rect(355, 580, 2, 100),
        pygame.Rect(715, 340, 20, 2),
        pygame.Rect(815, 335, 10, 2),
        pygame.Rect(750, 275, 2, 50),
        pygame.Rect(800, 275, 2, 50),
        pygame.Rect(750, 290, 50, 2)
    ]

    enemy_positions = []

# This function stores a rectangle in the hearts list at the position specified
hearts = []
def create_heart(pos):
    heart_rect = pygame.Rect(pos.x, pos.y, 20, 20)
    hearts.append({"rect": heart_rect})

# This function calls the create_heart() function at each of the heart positions
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
    {"speaker": "Tāne", "text": "Hello there, little spirit. Welcome to the afterlife!"}, # Format: "speaker", "text" 
    {"speaker": "Tāne", "text": "The journey ahead is dangerous. You'll need to face off against evil spirits to reach your whanau."},
    {"speaker": "Tāne", "text": "Use WASD to move and click to shoot!"},
    {"speaker": "Player", "text": "Thank you for advice."},
    {"speaker": "Tāne", "text": "Good luck on your journey!"}
]

maori_npc_dialogue = [
    {"speaker": "Tāne", "text": "Kia ora e te wairua iti. Nau mai ki te ao o muri!"}, # Format: "speaker", "text" 
    {"speaker": "Tāne", "text": "He kino te haerenga kei mua. Me whawhai koe ki nga wairua kino kia tae atu ki to whanau."},
    {"speaker": "Tāne", "text": "Whakamahia te WASD ki te neke ka paato ki te kopere!"},
    {"speaker": "Kaiwhakatangi", "text": "Mauruuru koe mo te tohutohu."},
    {"speaker": "Tāne", "text": "Kia pai to haerenga!"}
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

# function that makes a diagnal line by drawning multiple rectangles
def diagnal_line(length, start_x, start_y, x_step, y_step):
    for i in range(length):
        rect = pygame.Rect(start_x + i * x_step, start_y + i * y_step, 2, 2)
        collision_rects.append(rect)

# This function makes collisions for tree type 1
def draw_tree_type1(x, y):
    diagnal_line(29, x, y, 1, 1.5)
    diagnal_line(31, x, y, -1, 1.5)
    diagnal_line(27, x + 30, y + 45, 1, 5)
    diagnal_line(28, x - 30, y + 45, -0.5, 5)
    collision_rects.append(pygame.Rect(x - 42, y + 180, 100, 2))
    collision_rects.append(pygame.Rect(x, y + 180, 2, 17))
    collision_rects.append(pygame.Rect(x + 29, y + 180, 2, 17))
    collision_rects.append(pygame.Rect(x, y + 197, 31, 2))

# This cuntion makes collision lines for tree type 2
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

# Draw tree clollisions
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

# Draw all the diagnal collsion lines
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
                lines.append(' '.join(current_line)) # Adds the currentLine to the lines list
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
    if language == "en":
        indicator_text = "Click to continue..." if dialogue_index < len(npc_dialogue) - 1 else "Click to close" # Detects if its the last line. If not, then display "Click to continue...", if it is display "Click to close"
    elif language == "mi": 
        indicator_text = "Pāwhiri ko tonu..." if dialogue_index < len(npc_dialogue) - 1 else "Pāwhiri ko kati"
    indicator_surface = dialogue_font.render(indicator_text, True, (150, 150, 150))
    indicator_x = box_x + dialogue_box_width - indicator_surface.get_width() - dialogue_padding
    indicator_y = box_y + dialogue_box_height - 30
    surface.blit(indicator_surface, (indicator_x, indicator_y))

def draw_level_selector():
    """Draw the level selection menu and return a list of level button rects and the back button rect"""
    screen.blit(get_menu_background(), (0, 0))

    # Title
    title_font = pygame.font.Font(None, 80)
    if language == "en":
        title_text = title_font.render("Select Level", True, (255, 255, 255))
    elif language == "mi":
        title_text = title_font.render("Tīpakohia te Taumata", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 - 100))
    screen.blit(title_text, title_rect) 

    # 3 levels
    if language == "en":
        levels = ["Level 1", "Level 2", "Level 3"]
    elif language == "mi":
        levels = ["Taumata 1", "Taumata 2", "Taumata 3"]
    else:
        levels = ["Level 1", "Level 2", "Level 3"]
    button_font = pygame.font.Font(None, 60)
    button_width = 300
    button_height = 80
    button_spacing = 40
    buttons = []
    start_y = WINDOW_HEIGHT // 2  - ((button_height + button_spacing) * len(levels)) // 2

    mouse_pos = pygame.mouse.get_pos()  # Get mouse position once here

    for i, level_name in enumerate(levels):
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_y = start_y + i * (button_height + button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovering = button_rect.collidepoint(mouse_pos)
        button_color = (70, 130, 180) if is_hovering else (40, 80, 140)
        border_color = (100, 150, 200) if is_hovering else (80, 80, 120)
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, border_color, button_rect, 3)
        text_surface = button_font.render(level_name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        buttons.append((button_rect, level_name))

    # Back button
    back_button_font = pygame.font.Font(None, 50)
    if language == "en":
        back_text = back_button_font.render("Back", True, (255, 255, 255))
        back_button_width = 180
    elif language == "mi":
        back_text = back_button_font.render("Whakahoki", True, (255, 255, 255))
        back_button_width = 200
    back_button_height = 60
    back_button_x = (WINDOW_WIDTH - back_button_width) // 2
    back_button_y = start_y + len(levels) * (button_height + button_spacing) + 20
    back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
    is_hovering_back = back_button_rect.collidepoint(mouse_pos)
    back_button_color = (70, 130, 180) if is_hovering_back else (40, 80, 140)
    back_border_color = (100, 150, 200) if is_hovering_back else (80, 80, 120)
    pygame.draw.rect(screen, back_button_color, back_button_rect)
    pygame.draw.rect(screen, back_border_color, back_button_rect, 3)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)

    return buttons, back_button_rect

# Settings menu variables
sound_enabled = True  

def draw_settings_menu():
    """Draw the settings menu and return the sound toggle button rect, as well as the language toggle rect"""
    screen.blit(get_menu_background(), (0, 0)) 

    # Title
    title_font = pygame.font.Font(None, 80)
    if language == "en":
        title_text = title_font.render("Settings", True, (255, 255, 255))
    elif language == "mi":
        title_text = title_font.render("Kōwhiringa", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Language toggle button
    button_font = pygame.font.Font(None, 60)
    sound_button_width = 300
    sound_button_width_mi = 320
    lang_button_width = 500
    button_height = 80
    button_x = (WINDOW_WIDTH - sound_button_width) // 2
    lang_button_y = WINDOW_HEIGHT // 2 - button_height - 30
    if language == "en":
        lang_text = "Language: English"
    elif language == "mi":
        lang_text = "Language: Te Reo Māori"
    else:
        lang_text = f"Language: {language}"
    lang_button_rect = pygame.Rect(button_x - 100, lang_button_y, lang_button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    is_hovering_lang = lang_button_rect.collidepoint(mouse_pos)
    lang_button_color = (70, 130, 180) if is_hovering_lang else (40, 80, 140)
    lang_border_color = (100, 150, 200) if is_hovering_lang else (80, 80, 120)
    pygame.draw.rect(screen, lang_button_color, lang_button_rect)
    pygame.draw.rect(screen, lang_border_color, lang_button_rect, 3)
    lang_text_surface = button_font.render(lang_text, True, (255, 255, 255))
    lang_text_rect = lang_text_surface.get_rect(center=lang_button_rect.center)
    screen.blit(lang_text_surface, lang_text_rect)

    # Sound toggle button
    sound_button_y = WINDOW_HEIGHT // 2
    if language == "en":    
        sound_text = "Sound: ON" if sound_enabled else "Sound: OFF"
        sound_button_rect = pygame.Rect(button_x, sound_button_y, sound_button_width, button_height)
    elif language == "mi":
        sound_text = "Hīrea: Whakakā" if sound_enabled else "Hīrea: Whakaweto"
        sound_button_rect = pygame.Rect(button_x, sound_button_y, sound_button_width_mi, button_height)
    
    is_hovering = sound_button_rect.collidepoint(mouse_pos)
    button_color = (70, 130, 180) if is_hovering else (40, 80, 140)
    border_color = (100, 150, 200) if is_hovering else (80, 80, 120)
    pygame.draw.rect(screen, button_color, sound_button_rect)
    pygame.draw.rect(screen, border_color, sound_button_rect, 3)
    text_surface = button_font.render(sound_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=sound_button_rect.center)
    screen.blit(text_surface, text_rect)

    # Back button
    back_button_font = pygame.font.Font(None, 50)
    if language == "en":
        back_text = back_button_font.render("Back", True, (255, 255, 255))
        back_button_width = 180
    elif language  == "mi":
        back_text = back_button_font.render("Whakahoki",  True, (255, 255, 255))
        back_button_width = 200
    back_button_height = 60
    back_button_x = (WINDOW_WIDTH - back_button_width) // 2
    back_button_y = sound_button_y + button_height + 40
    back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
    is_hovering_back = back_button_rect.collidepoint(mouse_pos)
    back_button_color = (70, 130, 180) if is_hovering_back else (40, 80, 140)
    back_border_color = (100, 150, 200) if is_hovering_back else (80, 80, 120)
    pygame.draw.rect(screen, back_button_color, back_button_rect)
    pygame.draw.rect(screen, back_border_color, back_button_rect, 3)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)

    return lang_button_rect, sound_button_rect, back_button_rect

# Main loop
running = True
play_button_rect, settings_button_rect = None, None
level_buttons, back_button_rect = None, None
sound_button_rect, settings_back_button_rect = None, None
while running:
    dt = clock.tick(60) / 1000
    # Draw screen and cache button rects before event handling
    if game_state == "menu":
        play_button_rect, settings_button_rect = draw_menu()
    elif game_state == "level_select":
        level_buttons, back_button_rect = draw_level_selector()
    elif game_state == "settings":
        lang_button_rect, sound_button_rect, settings_back_button_rect = draw_settings_menu()
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Menu interactions
        if game_state == "menu":
            soundtrack_2.stop()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # If player left clicks
                mouse_pos = pygame.mouse.get_pos()
                if play_button_rect and play_button_rect.collidepoint(mouse_pos):
                    game_state = "level_select"
                    player_lives = 3
                    interacted_with_npc = False
                    level_1_spawned = False
                    reset_enemies()
                    player_pos = pygame.Vector2(1150, 950)
                    player_rect.center = player_pos
                    trumpet.play()
                    # Reset objective when starting a new run
                    objective = 'Talk to NPC'
                if settings_button_rect and settings_button_rect.collidepoint(mouse_pos):
                    game_state = "settings"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False  # Exit game from main menu
        # Settings interactions
        elif game_state == "settings":
            soundtrack_2.stop()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if lang_button_rect and lang_button_rect.collidepoint(mouse_pos):
                    language = "mi" if language == "en" else "en"
                if sound_button_rect and sound_button_rect.collidepoint(mouse_pos):
                    sound_enabled = not sound_enabled
                    # Set sound volume accordingly
                    trumpet.set_volume(0.3 if sound_enabled else 0.0)
                    water_drip.set_volume(1.0 if sound_enabled else 0.0)
                    soundtrack_1.set_volume(0.5 if sound_enabled else 0.0)
                    soundtrack_2.set_volume(0.5 if sound_enabled else 0.0)
                if settings_back_button_rect and settings_back_button_rect.collidepoint(mouse_pos):
                    game_state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "menu"
        # Level selector interactions
        elif game_state == "level_select":
            soundtrack_2.stop()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button_rect, level_name in level_buttons or []:
                    if button_rect.collidepoint(mouse_pos):
                        if (language == "en" and level_name == "Level 1") or (language == "mi" and level_name == "Taumata 1"):
                            selected_level = level_name
                            game_state = "playing"
                            game_start_time = pygame.time.get_ticks()
                            # Reset objective when entering gameplay
                            objective = 'Talk to NPC'
                            # Play soundtrack 2 (one loop, then repeat)
                            soundtrack_2.stop()
                            soundtrack_2.play(loops=0)
                        # Level 2 and Level 3 do nothing for now

                        elif (language == "en" and level_name == "Level 2") or (language == "mi" and level_name == "Taumata 2"):
                            in_level_2 = True
                            game_state = "playing"
                            interacted_with_npc = True
                            level_2()



                if back_button_rect and back_button_rect.collidepoint(mouse_pos):
                    game_state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "menu"  # Go back to main menu from level select

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
                    projectile_rect = projectile_image.get_rect(center = player_pos) # Create projectile rectangle for collisions
                    mouse_pos = pygame.mouse.get_pos()
                    # Convert mouse position to world coordinates considering zoom
                    mouse_world_x = (mouse_pos[0] / ZOOM) + camera.x
                    mouse_world_y = (mouse_pos[1] / ZOOM) + camera.y
                    mouse_world_pos = pygame.Vector2(mouse_world_x, mouse_world_y)
                    
                    # Get the direction the projectile needs to travel to go towards the player
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

        # When the game over screen is displayed, wait 2 seconds and then return to menu
        if pygame.time.get_ticks() - game_over_time > 2000:
            game_state = "menu"
            game_over_time = 0
            soundtrack_1.stop()
            # Reset objective when returning to menu after game over
            objective = 'Talk to NPC'
        
    elif game_state == "playing":
        keys = pygame.key.get_pressed()

        # Move vertically - If player is not talking to the NPC, Check if they are pressing W or S and move them accordingly.
        old_y = player_pos.y
        if not dialogue_active:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_pos.y -= player_vel * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_pos.y += player_vel * dt

        player_rect.center = player_pos  # Update rect position
        
        # Simple collision detection for vertical movement
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                if rect == pygame.Rect(755, 1160, 60, 2) and not in_level_2:
                    if len(enemies) == 0 and interacted_with_npc:
                        level_2()

                elif rect == pygame.Rect(750, 290, 50, 2) and in_level_2:
                    if not game_finished:
                        game_finished = True
                        end_time = pygame.time.get_ticks()

                player_pos.y = old_y
                player_rect.center = player_pos
                break

        # Move horizontally - If player is not talking to the NPC, Check if they are pressing A or D and move them accordingly.
        old_x = player_pos.x
        if not dialogue_active:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_pos.x -= player_vel * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_pos.x += player_vel * dt

        player_rect.center = player_pos  # Update rect position
        
        
        # Simple collision detection for horizontal movement
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                if rect == pygame.Rect(755, 1160, 60, 2) and not in_level_2:
                    if len(enemies) == 0 and interacted_with_npc:
                        level_2()

                elif rect == pygame.Rect(750, 290, 50, 2) and in_level_2:
                        if not game_finished:
                            game_finished = True
                            end_time = pygame.time.get_ticks()

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

        render_surface, darkness_surface = get_render_surfaces()

        # Draw everything to render_surface (world coordinates)
        if in_level_2:
            lvl2_background_img = pygame.image.load('lvl2_background.png').convert_alpha() # Load level 2 background image
            lvl2_background_img = pygame.transform.scale(lvl2_background_img, (2000, 1300)) # Set background image size
            render_surface.blit(lvl2_background_img, (0, 0), area=pygame.Rect(camera.x, camera.y, camera.width, camera.height)) # Draw the background image to the screen

        else:
            render_surface.blit(background_img, (0, 0), area=pygame.Rect(camera.x, camera.y, camera.width, camera.height))

        # Draw NPC at camera-relative position
        npc_screen_pos = camera.apply(npc_pos)
        npc_draw_rect = npc_img.get_rect(center=npc_screen_pos)
        if not in_level_2:
            render_surface.blit(npc_img, npc_draw_rect)

        # Draw interaction prompt if player is close to NPC (and not in dialogue)
        if not dialogue_active and not interacted_with_npc:
            distance = player_pos.distance_to(npc_pos)
            if distance <= interaction_distance:
                if language == "en":
                    prompt_text = dialogue_font.render("Press E to talk", True, (255, 255, 255))
                elif language == "mi":
                    prompt_text = dialogue_font.render("Perehi E ko kōrerorero", True, (255, 255, 255))
                prompt_pos = (npc_screen_pos.x - prompt_text.get_width() // 2, 
                             npc_screen_pos.y - 50)
                render_surface.blit(prompt_text, prompt_pos)

        # Create a copy of the portal rectangle, and then use camera.apply so it is fixed to the background
        if in_level_2:
            portal_rect = pygame.Rect(710, 230, 150, 150) # Rectangle for portal

        else:
            portal_rect = pygame.Rect(730, 1100, 150, 150) # Rectangle for portal

        portal_rect2 = portal_rect.copy()
        portal_rect2.topleft = camera.apply(pygame.Vector2(portal_rect2.topleft))

        render_surface.blit(portal_img, portal_rect2.topleft) # Draw portal to the screen

        # Draw player at camera-relative position
        player_screen_pos = camera.apply(player_pos)
        player_draw_rect = player.get_rect(center=player_screen_pos)
        render_surface.blit(player, player_draw_rect)

        # Blit darkness surface on top of render_surface
        screen.blit(render_surface, (0, 0))
        screen.blit(darkness_surface, (0, 0))

        # Draw the collision rectangles in a way that they do move with the camera, but stay fixed to the map
        for rect in collision_rects:
            cam_rect = rect.copy()
            cam_rect.topleft = camera.apply(pygame.Vector2(rect.topleft))
            pygame.draw.rect(render_surface, 'red', cam_rect, -1)


        to_remove = [] # List of projectiles to be removed from the screen
        deads = [] # List to store dead enemies
        for enemy in enemies:
            enemy_screen_pos = camera.apply(pygame.Vector2(enemy["rect"].topleft)) # Draw each enemy in a way that it doesnt move with camer
            render_surface.blit(enemy_image, enemy_screen_pos)

            enemy_pos = pygame.Vector2(enemy["rect"].center)# Get the enemies position
            enemy_direction = player_pos - enemy_pos # Get the direction to the player
            distance = enemy_direction.length()

            # If the player is within a 300 pixel radius of the enemy, the enemy will follow the player and shoot a projectile at them once a second
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

                # If the enemy is colliding with a collision rectangle, set enemy_moving to False
                enemy_moving = True
                for rect in collision_rects:
                    if rect.colliderect(enemy["rect"]):
                        enemy_moving = False

                # If enemy_moving is set to False, set the enemy velocity to 0 so it can't move anymore
                if not enemy_moving:
                    enemy_vel = 0

                # If the enemy_moving is True, set enemy velocity back to normal
                elif enemy_moving:
                    enemy_vel = 100

            # If the enemy is hit by a player projectile, remove the enemy and the projectile
            for proj in projectiles:
                if proj["rect"].colliderect(enemy["rect"]):
                    deads.append(enemy)

                    if proj in projectiles:
                        projectiles.remove(proj)

            # Remove all the enemies in the deads list from the enemies list 
            for dead in deads:
                if dead in enemies:
                    enemies.remove(dead)

        for proj in enemy_projectiles:
            # Move the enemy projectiles relative to the screen
            proj["rect"].centerx += proj["velocity"].x * dt
            proj["rect"].centery += proj["velocity"].y * dt

            cam_rect = proj["rect"].copy()
            cam_rect.topleft = camera.apply(pygame.Vector2(proj["rect"].topleft))
            render_surface.blit(enemy_proj_image, cam_rect.topleft)

            # If the player is hit by an enemy projectile, remove a life and delete the projectile
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

        # Move the projectiles relative to the screen
        for proj in projectiles:
            proj["rect"].centerx += proj["velocity"].x * projectile_vel * dt
            proj["rect"].centery += proj["velocity"].y * projectile_vel * dt

            proj_rect = proj["rect"].copy()
            proj_rect.topleft = camera.apply(pygame.Vector2(proj["rect"].topleft))
            render_surface.blit(projectile_image, proj_rect.topleft)

            # If the projectile hits a collisions rectangle, delete it
            for rect in collision_rects:
                if rect.colliderect(proj["rect"]):
                    to_remove.append(proj)
                    break

            for proj in to_remove:
                if proj in projectiles:
                    projectiles.remove(proj)

        # If the player lives are equal to zero, display the game over screen
        if player_lives == 0:
            game_state = "game_over"
            game_over_time = pygame.time.get_ticks()

        # If the player has interacted with the npc, draw level 1
        if interacted_with_npc:
            if not level_1_spawned:
                    level_1()
                    level_1_spawned = True
                    # Only set the 'kill all enemies' objective if we're not in level 2
                    if not in_level_2:
                        if language == "en":
                            objective = 'Objective: Kill all enemies'
                        elif language == "mi":
                            objective = "whāinga poto: tinei katoa ngangare"

        hearts_to_remove = []
        # If the player has less than 3 lives, draw hearts on the screen
        if player_lives < 3:
            for heart in hearts:
                heart_rect = heart["rect"].copy()
                heart_rect.topleft = camera.apply(pygame.Vector2(heart["rect"].topleft))
                render_surface.blit(heart_img, heart_rect.topleft)

                # If the player touches a heart, add it to the player lives and remove it from the screen
                if player_rect.colliderect(heart["rect"]):
                    player_lives += 1
                    hearts_to_remove.append(heart)

            for heart in hearts_to_remove:
                if heart in hearts:
                    hearts.remove(heart)

            
            # (Hint rendering moved later so it isn't affected by darkness)
        
        if lighting_enabled:
            # Fill the game with darkness
            darkness_surface.fill(darkness_colour)

            light_center = (int(player_screen_pos.x), int(player_screen_pos.y))
            max_radius = 150  # The outermost edge of the light
            step = 6  

            for radius in range(max_radius, 0, -step): # Much fewer iterations now
                # Calculate brightness for the current ring
                light_intensity = 3
                normalized_radius = radius / max_radius
                brightness = int(light_intensity * 255 * (1 - normalized_radius**1.2))

                # Ensure brightness stays within the valid range of 0 and 255
                brightness = max(0, min(255, brightness))

                # RBG of the light
                light_color = (brightness, brightness, brightness)

                # Draw the circle for this ring of light onto our light map.
                pygame.draw.circle(darkness_surface, light_color, light_center, radius)

            render_surface.blit(darkness_surface, (0,0), special_flags=pygame.BLEND_MULT)


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

                temp_rect = pygame.Rect(0, 0, 0, 0)
                temp_rect.center = (portal_rect.centerx - 13, portal_rect.centery - 10)
                portal_center_screen = camera.apply(temp_rect)

                if len(enemies) == 0 and interacted_with_npc and not in_level_2:
                    pygame.draw.circle(darkness_surface, light_color, portal_center_screen, 90)
                    if language == "en":
                        objective = 'Objective: Go to the portal'
                    elif language == "mi":
                        objective = 'whāinga poto: Haere ki te tomokanga'
                    else:
                        objective = 'Objective: Go to the portal'


            render_surface.blit(darkness_surface, (0,0), special_flags=pygame.BLEND_MULT)

        # Scale render_surface to screen for zoom effect
        scaled_surface = pygame.transform.smoothscale(render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        # Draw dialogue box on top of everything (if active)
        if dialogue_active:
            if language == "en":
                current_dialogue = npc_dialogue[dialogue_index]
                draw_dialogue_box(screen, current_dialogue["speaker"], current_dialogue["text"])
            elif language == "mi":
                current_dialogue = maori_npc_dialogue[dialogue_index]
                draw_dialogue_box(screen, current_dialogue["speaker"], current_dialogue["text"])
        
        # Draw timer on top left (always visible during gameplay)
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - game_start_time) // 1000
        if language == "en":
            timer_text = timer_font.render(f"Timer: {elapsed_seconds}s", True, (255, 255, 255))
        elif language == "mi": 
            timer_text = timer_font.render(f"Tāima: {elapsed_seconds}s", True, (255, 255, 255))
        
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

        # Draw hint on the very top layer so darkness does not obscure it
        if not interacted_with_npc and not dialogue_active:
            if language == "en":
                hint_str = "Hint: Talk to the NPC to begin your journey!"
            elif language == "mi":
                hint_str = "Tohuto: Kōrero ki te NPC hei tīmata i tō haerenga!"
            else:
                hint_str = "Hint: Talk to the NPC to begin your journey!"
            hint_font = pygame.font.Font(None, 32)
            hint_text = hint_font.render(hint_str, True, (255, 255, 0))
            hint_bg = pygame.Surface((hint_text.get_width() + 20, hint_text.get_height() + 10), pygame.SRCALPHA)
            hint_bg.fill((0, 0, 0, 180))
            screen.blit(hint_bg, ((WINDOW_WIDTH - hint_bg.get_width()) // 2, 20))
            screen.blit(hint_text, ((WINDOW_WIDTH - hint_text.get_width()) // 2, 25))

        # Draw objective at top center if it's been updated (skip initial 'Talk to NPC')
        if objective and objective != 'Talk to NPC':
            obj_text = objective_font.render(objective, True, (255, 255, 255))
            obj_bg = pygame.Surface((obj_text.get_width() + 20, obj_text.get_height() + 10), pygame.SRCALPHA)
            obj_bg.fill((0, 0, 0, 180))
            obj_y = 60  # position slightly below the hint
            screen.blit(obj_bg, ((WINDOW_WIDTH - obj_bg.get_width()) // 2, obj_y))
            screen.blit(obj_text, ((WINDOW_WIDTH - obj_text.get_width()) // 2, obj_y + 5))

    # Check if soundtrack_1 finished and repeat if needed
    if selected_level == "Level 1":
        if not pygame.mixer.get_busy():
            soundtrack_2.play(loops=0)

    if game_finished:
        end_screen()

    print(pygame.mouse.get_pos())

    # Update display
    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()

