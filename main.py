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

ZOOM = 1.2  # zoom level 

# Camera dead zone - Alex
CAMERA_MARGIN_X = 120
CAMERA_MARGIN_Y = 80


# Game Menu 
game_state = "menu"

# Timer variables
game_start_time = 0
timer_font = pygame.font.Font(None, 36)
timer_border_location = 10
timer_location = 15


# Lighting variables
lighting_enabled = True
light_sources = []
darkness_colour = (20,20,40)

def draw_menu(): 
    for y in range(0, WINDOW_HEIGHT, 2):    
        progress = y / WINDOW_HEIGHT
        colour_value = (
            int(start_colour[0] + (end_colour[0] - start_colour[0]) * progress),
            int(start_colour[1] + (end_colour[1] - start_colour[1]) * progress),
            int(start_colour[2] + (end_colour[2] - start_colour[2]) * progress)
        )

        pygame.draw.rect(screen, colour_value, (0, y, WINDOW_WIDTH, 5))

    
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
background_img = pygame.image.load("background.png").convert_alpha()
BG_WIDTH, BG_HEIGHT = background_img.get_size()

#player - Riley
player = pygame.image.load('sprites/player.png').convert_alpha() # load the player image
player = pygame.transform.scale(player, (60, 60)) # set player size
player_pos = pygame.Vector2(100, 550) # set initial player position
player_rect = pygame.Rect(0, 0, 30, 30) # Player rectangle for collisions
player_rect.center = player_pos
player_vel = 4 # player speed


# Load heart icon
heart_img = pygame.image.load("heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30,30))

# Player lives - Alex
player_lives = 3
health_font = pygame.font.Font(None, 36)

# NPC - Alex
npc_img = pygame.image.load('sprites/NPC.png').convert_alpha()
npc_img = pygame.transform.scale(npc_img, (70, 70))
npc_pos = pygame.Vector2(BG_WIDTH // 2, BG_HEIGHT // 2)
npc_rect = npc_img.get_rect(center=npc_pos)

# projectiles - Riley
projectile_image = pygame.image.load('sprites/player_projectile.png').convert_alpha() # saves the projectile image
projectiles = [] # create a list to store information for projectiles (eg position)
projectile_vel = 2 # set the speed of the projectile

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
darkness_surface = pygame.Surface((camera.width, camera.height))

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
    
# List of rectangles for collision - Riley
collision_rects = [
    pygame.Rect(553, 530, 357, 217),
    pygame.Rect(540, 200, 2, 340),
    pygame.Rect(913, 160, 2, 350),
    pygame.Rect(913, 150, 335, 2),
    pygame.Rect(915, 337, 670, 2),
    pygame.Rect(233, 337, 317, 2),
    pygame.Rect(715, 430, 42, 2),
    pygame.Rect(715, 460, 55, 2)
]

# function for making diagnal collision lines
def diagnal_line(length, start_x, start_y, x_step, y_step):
    for i in range(length):
        rect = pygame.Rect(start_x + i * x_step, start_y + i * y_step, 2, 2)
        collision_rects.append(rect)

# diagnal collision lines
diagnal_line(165, 1250, 175, 2, 1)
diagnal_line(140, 550, 190, -2.2, 1)
diagnal_line(175, 195, 165, 2, -1)
diagnal_line(185, 1300, 0, 2, 1)

# function to make collisions for tree type 1
def draw_tree_type1(tip_x, tip_y):
    diagnal_line(45, tip_x, tip_y, 1, 1.3)
    diagnal_line(50, tip_x, tip_y, -1, 1.3)
    diagnal_line(53, tip_x + 40, tip_y + 55, 1, 4)
    diagnal_line(34, tip_x - 45, tip_y + 55, -1, 6)
    diagnal_line(23, tip_x - 80, tip_y + 255, 1, 1)
    diagnal_line(50, tip_x - 55, tip_y + 275, 1, -0.01)
    collision_rects.append(pygame.Rect(tip_x, tip_y + 260, 2, 30))
    collision_rects.append(pygame.Rect(tip_x, tip_y + 290, 30, 2))
    collision_rects.append(pygame.Rect(tip_x + 30, tip_y + 260, 2, 30))
    collision_rects.append(pygame.Rect(tip_x + 30, tip_y + 260, 60, 2))

# function to make collisions for tree type 2
def draw_tree_type2(tip_x, tip_y):
    diagnal_line(42, tip_x, tip_y, 1.5, 2)
    diagnal_line(42, tip_x, tip_y, -1.5, 2)
    diagnal_line(37, tip_x + 60, tip_y + 80, 1, 2)
    diagnal_line(70, tip_x + 95, tip_y + 155, 0.2, 2)
    diagnal_line(37, tip_x - 60, tip_y + 80, -1, 2)
    diagnal_line(70, tip_x - 95, tip_y + 155, -0.2, 2)
    collision_rects.append(pygame.Rect(tip_x - 110, tip_y + 295, 220, 2))
    collision_rects.append(pygame.Rect(tip_x - 20, tip_y + 300, 2, 30))
    collision_rects.append(pygame.Rect(tip_x + 20, tip_y + 300, 2, 30))
    collision_rects.append(pygame.Rect(tip_x - 20, tip_y + 330, 42, 2))

# tree type 1 collisions
draw_tree_type1(135, 188)
draw_tree_type1(1222, 230)
draw_tree_type1(1040, 183)

# tree type 2 collisions
draw_tree_type2(380, 146)
draw_tree_type2(1425, 150)
draw_tree_type2(1469, 510)
draw_tree_type2(1785, 460)

# Main loop
running = True
while running:
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
                render_surface = pygame.Surface((camera.width, camera.height))

            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                camera.width = int(WINDOW_WIDTH / ZOOM)
                camera.height = int(WINDOW_HEIGHT / ZOOM)
                render_surface = pygame.Surface((camera.width, camera.height))

            # Handle dialogue interaction
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e: 
                if not dialogue_active:
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
                        direction = direction.normalize() * 10
                        projectiles.append({"rect": projectile_rect, "velocity": direction})

    # Handle different game states
    if game_state == "menu":
        # Draw the menu
        draw_menu()
        
    elif game_state == "playing":
        # Game logic (only run when playing)
        keys = pygame.key.get_pressed()
        
        # Move vertically
        old_y = player_pos.y
        if not dialogue_active:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_pos.y -= player_vel
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_pos.y += player_vel

        player_rect.center = player_pos  # Update rect position
        # If the player touches a collision rectangle vertically, stop them from moving further
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                player_pos.y = old_y
                player_rect.center = player_pos
                break

        # Move horizontally
        old_x = player_pos.x
        if not dialogue_active:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_pos.x -= player_vel
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_pos.x += player_vel

        player_rect.center = player_pos  # Update rect position
        # if the player touches a collision rectangle horizontally, stop them from moving further
        for rect in collision_rects:
            if player_rect.colliderect(rect):
                player_pos.x = old_x
                player_rect.center = player_pos
                break

        # Close the game if the player presses escape - Riley
        if keys[pygame.K_ESCAPE]:
            exit() # Return to menu instead of exiting

        # Clamp player position to background - Riley
        if player_pos.x <= 30: # If player goes too far left, stop them
            player_pos.x = 30

        if player_pos.x >= BG_WIDTH - 20: # If player goes too far right, stop them
            player_pos.x = BG_WIDTH - 20

        if player_pos.y <= 20: # If the player goes too far up, stop them
            player_pos.y = 20

        if player_pos.y >= 880: # If the player goes too far down, stop them
            player_pos.y = 880

        player_pos.x = max(0, min(player_pos.x, BG_WIDTH))
        player_pos.y = max(0, min(player_pos.y, BG_HEIGHT))

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

        # Draw interaction prompt if player is close to NPC (and not in dialogue)
        if not dialogue_active:
            distance = player_pos.distance_to(npc_pos)
            if distance <= interaction_distance:
                prompt_text = dialogue_font.render("Press E to talk", True, (255, 255, 255))
                prompt_pos = (npc_screen_pos.x - prompt_text.get_width() // 2, 
                             npc_screen_pos.y - 50)
                render_surface.blit(prompt_text, prompt_pos)


        # Draw player at camera-relative position
        player_screen_pos = camera.apply(player_pos)
        player_draw_rect = player.get_rect(center=player_screen_pos)
        render_surface.blit(player, player_draw_rect)
        
        # Lighting
        if lighting_enabled:
            # Fill the game with darkness
            darkness_surface.fill(darkness_colour)


            light_center = (int(player_screen_pos.x), int(player_screen_pos.y))
            max_radius = 250  # The outermost edge of the light
            step = 2 # How quick the blending is

            for radius in range(max_radius, 0, -step): # for each radius (out of 180 to 0, and how quickly it goes down by)
                # Calculate brightness for the current ring
                # Brightness increases, as radius gets smaller
                light_intensity = 2
                normalized_radius = radius / max_radius
                brightness = int(light_intensity * 255 * (1 - normalized_radius**1.2))

                # Ensure brightness stays within the valid range of 0 and 255
                
                brightness = max(0, min(255, brightness))

                # RBG of the light
                light_color = (brightness, brightness, brightness)

                # Draw the circle for this ring of light onto our light map.
                pygame.draw.circle(darkness_surface, light_color, light_center, radius)


            render_surface.blit(darkness_surface, (0,0), special_flags=pygame.BLEND_MULT)

        # Draw the collision rectangles in a way that they do move with the camera, but stay fixed to the map
        for rect in collision_rects:
            cam_rect = rect.copy()
            cam_rect.topleft = camera.apply(pygame.Vector2(rect.topleft))
            pygame.draw.rect(render_surface, 'red', cam_rect, -1)

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
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()