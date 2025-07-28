import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('test')
clock = pygame.time.Clock()

background = pygame.Surface((500, 500))

player = pygame.Surface((40, 40))
player.fill('red')
player_rect = player.get_rect(center = (250, 250))

projectile_image = pygame.image.load('sprites/player_projectile.png').convert_alpha()
pygame.transform.scale(projectile_image, (20, 20))
projectiles = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            projectile_rect = projectile_image.get_rect(center = (250, 250))
            mouse_pos = pygame.mouse.get_pos()
            direction = pygame.Vector2(mouse_pos) - pygame.Vector2(250, 250)
            direction = direction.normalize() * 2 
            projectiles.append({"rect": projectile_rect, "velocity": direction})

    screen.blit(background, (0, 0))
    screen.blit(player, player_rect)

    for proj in projectiles:
        proj["rect"].centerx += proj["velocity"].x
        proj["rect"].centery += proj["velocity"].y
        screen.blit(projectile_image, proj["rect"])

    pygame.display.update()
    clock.tick(60)
