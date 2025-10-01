import pygame
import math
from configs.config_main import *
from environment.map import world_map
from colors import *
from textures import texture_manager
from player import Player
from raycasting import cast_rays_sector  # Import the function

pygame.init()

surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid-Based FPS Engine")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

player = Player()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    player.update_movement()

    surface.fill(BLACK)
    
 
    cast_rays_sector(surface, player.position, player.angle, NUMBER_OF_RAYS)

    # Debug info - show grid position and direction
    direction_names = ["North", "East", "South", "West"]
    debug_text = f"Grid: ({player.grid_x}, {player.grid_y}) Facing: {direction_names[player.direction]}"
    text_surface = font.render(debug_text, True, WHITE)
    surface.blit(text_surface, (10, 10))

    pygame.display.flip()
    clock.tick(TARGET_FPS)