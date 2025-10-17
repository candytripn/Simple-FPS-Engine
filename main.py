import pygame
import math
from configs.config_main import *
from environment.map import world_map, switch_map, get_current_map
from colors import *
from textures import texture_manager
from player import Player
from raycasting import cast_rays_sector 
from SpriteSheet import SpriteSheet, Sprite, Enemy, Boss  # Import all classes

pygame.init()

surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid-Based FPS Engine")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)P``

player = Player()
ceiling_correction_factor = 1.0
angle_correction_power = 1.0

# Create different sprite types
sprites = []
combat_sprite = None  # Store the sprite we're fighting

# Load demon enemy sprite
try:
    demon_sprite_sheet = SpriteSheet('C:\\intro to programming\\Simple-FPS-Engine\\Flying Demon 2D Pixel Art\\Sprites\\with_outline\\IDLE.png')
    demon_animation = demon_sprite_sheet.load_strip((0, 0, 82, 65), 4)
    demon_enemy = Enemy(6, 2, demon_sprite_sheet, demon_animation, scale_factor=0.2, enemy_type="demon")
    sprites.append(demon_enemy)
    print(f"Successfully loaded {demon_enemy.enemy_type} enemy at grid ({demon_enemy.x}, {demon_enemy.y})")
except Exception as e:
    print(f"Failed to load demon sprite: {e}")

# Load boss sprite (you can use the same spritesheet for now, or load a different one)
try:
    boss_animation = demon_sprite_sheet.load_strip((0, 0, 82, 65), 4)  # Same animation for now
    demon_boss = Boss(8, 3, demon_sprite_sheet, boss_animation, scale_factor=0.4, boss_type="demon_lord")
    sprites.append(demon_boss)
    print(f"Successfully loaded {demon_boss.enemy_type} boss at grid ({demon_boss.x}, {demon_boss.y})")
except Exception as e:
    print(f"Failed to load boss sprite: {e}")

def enter_combat_with_sprite(encountered_sprite):
    """Transport player to combat arena and position sprite in front of player"""
    global combat_sprite
    
    # Store the sprite we're fighting
    combat_sprite = encountered_sprite
    
    # Switch to combat arena
    switch_map("combat_arena")
    player.move_to_grid(1, 1)
    player.direction = 1
    player.angle = DIRECTIONS[player.direction]
    player.current_map = get_current_map()
    player.in_combat = True
    print(f"Switched to: {player.current_map}")
    
    # Position the encountered sprite in front of the player
    forward_x, forward_y = player.get_forward_position()
    encountered_sprite.move_to(forward_x, forward_y)
    
    # Create a temporary sprite list with only the combat sprite
    global sprites
    sprites = [encountered_sprite]  # Only show the combat sprite
    
    print(f"Entering combat with {encountered_sprite.enemy_type}!")
    print(f"Player at ({player.grid_x}, {player.grid_y}), {encountered_sprite.enemy_type} at ({encountered_sprite.x}, {encountered_sprite.y})")

def exit_combat():
    """Return to dungeon and restore all sprites"""
    global sprites, combat_sprite
    
    switch_map("dungeon_level_1")
    player.move_to_grid(restore_point[0], restore_point[1])
    player.direction = 0
    player.angle = DIRECTIONS[player.direction]
    player.current_map = get_current_map()
    
    # Restore all sprites to their original positions
    sprites = []
    try:
        demon_sprite_sheet = SpriteSheet('C:\\intro to programming\\Simple-FPS-Engine\\Flying Demon 2D Pixel Art\\Sprites\\with_outline\\IDLE.png')
        demon_animation = demon_sprite_sheet.load_strip((0, 0, 82, 65), 4)
        demon_enemy = Enemy(6, 2, demon_sprite_sheet, demon_animation, scale_factor=0.2, enemy_type="demon")
        sprites.append(demon_enemy)
        
        boss_animation = demon_sprite_sheet.load_strip((0, 0, 82, 65), 4)
        demon_boss = Boss(8, 3, demon_sprite_sheet, boss_animation, scale_factor=0.4, boss_type="demon_lord")
        sprites.append(demon_boss)
    except Exception as e:
        print(f"Failed to reload sprites: {e}")
    
    combat_sprite = None
    player.in_combat = False
    print("Exited combat, returned to dungeon")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                ceiling_correction_factor -= 0.01
                print(f"Ceiling Correction Factor: {ceiling_correction_factor:.3f}")
            elif event.key == pygame.K_2:
                ceiling_correction_factor += 0.01
                print(f"Ceiling Correction Factor: {ceiling_correction_factor:.3f}")
            elif event.key == pygame.K_3:
                angle_correction_power -= 0.05
                print(f"Angle Correction Power: {angle_correction_power:.3f}")
            elif event.key == pygame.K_4:
                angle_correction_power += 0.05
                print(f"Angle Correction Power: {angle_correction_power:.3f}")
            elif event.key == pygame.K_m:  # Switch to combat arena manually
                switch_map("combat_arena")
                player.move_to_grid(1, 1)
                player.direction = 1
                player.angle = DIRECTIONS[player.direction]
                player.current_map = get_current_map()
                print(f"Switched to: {player.current_map}")
            elif event.key == pygame.K_n:  # Switch to boss room manually
                switch_map("boss_room")
                player.move_to_grid(8, 3)
                player.direction = 0
                player.angle = DIRECTIONS[player.direction]
                player.current_map = get_current_map()
                print(f"Switched to: {player.current_map}")
            elif event.key == pygame.K_b:  # Switch back to dungeon manually
                exit_combat()  # Use the exit_combat function
            elif event.key == pygame.K_e:  # Exit combat key
                if combat_sprite:
                    exit_combat()

    player.update_movement()
    
    # Update all sprites
    for sprite in sprites:
        sprite.update()

    surface.fill(BLACK)
    
    from environment.map import world_map
    cast_rays_sector(surface, player.position, player.angle, NUMBER_OF_RAYS, world_map, sprites, ceiling_correction_factor, angle_correction_power)

    # Debug info
    direction_names = ["North", "East", "South", "West"]
    debug_text = f"Grid: ({player.grid_x}, {player.grid_y}) Facing: {direction_names[player.direction]}"
    text_surface = font.render(debug_text, True, WHITE)
    surface.blit(text_surface, (10, 10))
    
    map_text = f"Current Map: {get_current_map()}"
    map_surface = font.render(map_text, True, WHITE)
    surface.blit(map_surface, (10, 90))
    
    # Show combat status
    if combat_sprite:
        combat_text = f"IN COMBAT! Press E to exit"
        combat_surface = font.render(combat_text, True, (255, 0, 0))  # Red text
        surface.blit(combat_surface, (10, 130))
    
    # Show sprite info with types
    y_offset = 50
    for sprite in sprites:
        if sprite.sprite_type == "enemy":
            sprite_text = f"{sprite.enemy_type} (HP: {sprite.health}/{sprite.max_health}) at ({sprite.x}, {sprite.y})"
        elif sprite.sprite_type == "boss":
            sprite_text = f"BOSS {sprite.enemy_type} (HP: {sprite.health}/{sprite.max_health}) at ({sprite.x}, {sprite.y})"
        else:
            sprite_text = f"{sprite.sprite_type} at ({sprite.x}, {sprite.y})"
        
        sprite_surface = font.render(sprite_text, True, WHITE)
        surface.blit(sprite_surface, (10, y_offset))
        y_offset += 25

    pygame.display.flip()
    clock.tick(TARGET_FPS)
    
    # Check for collisions with different sprite types
    for sprite in sprites:
        if (player.grid_x, player.grid_y) == sprite.position and sprite.is_alive:
            # Only enter combat if we're not already in combat
            if not combat_sprite:
                restore_point = (player.grid_x, player.grid_y)
                restore_angle = player.angle
                enter_combat_with_sprite(sprite)
            break
