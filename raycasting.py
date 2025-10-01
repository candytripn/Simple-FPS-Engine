import pygame
import math
from configs.config_main import *
from environment.map import world_map
from colors import *
from textures import texture_manager

def cast_rays_sector(surface, position, angle, rays_count):
    current_angle = angle - HALF_FOV
    xo, yo = position

    # No longer draw sky - we'll draw ceiling per ray
    wall_texture = texture_manager.get_texture('wall')
    floor_texture = texture_manager.get_texture('floor')
    ceiling_texture = texture_manager.get_texture('ceiling')

    for ray in range(rays_count):
        sin_a = math.sin(current_angle)
        cos_a = math.cos(current_angle)

        wall_hit = False
        
        for depth in range(0, MAX_DEPTH, 1):  # Step by 1 for better precision
            x = xo + depth * cos_a
            y = yo + depth * sin_a

            # Simple tile collision detection
            target_tile = (x // TILE_SIZE * TILE_SIZE, y // TILE_SIZE * TILE_SIZE)
            if target_tile in world_map:
                # FISH-EYE CORRECTION: Apply cosine correction to remove distortion
                corrected_depth = depth * math.cos(current_angle - angle)
                
                # Prevent division by zero or negative values
                if corrected_depth <= 0:
                    corrected_depth = 1

                projection_height = PROJECTION_COEF / corrected_depth
                
                # Calculate texture coordinate for wall
                # Determine which wall face we hit (horizontal or vertical)
                hit_x = x % TILE_SIZE
                hit_y = y % TILE_SIZE
                
                # Better texture coordinate calculation
                if abs(hit_x) < abs(hit_y - TILE_SIZE) and abs(hit_x - TILE_SIZE) < abs(hit_y - TILE_SIZE):
                    # Hit vertical wall (left or right side)
                    texture_x = int(hit_y) % TEXTURE_WIDTH
                else:
                    # Hit horizontal wall (top or bottom side)
                    texture_x = int(hit_x) % TEXTURE_WIDTH
                
                # Ensure texture_x is within bounds
                texture_x = max(0, min(TEXTURE_WIDTH - 1, texture_x))
                
                # Draw textured wall column
                wall_start = int(HALF_SCREEN_HEIGHT - projection_height // 2)
                wall_end = int(HALF_SCREEN_HEIGHT + projection_height // 2)
                
                # Clamp to screen bounds
                wall_start = max(0, wall_start)
                wall_end = min(SCREEN_HEIGHT, wall_end)
                
                wall_height = wall_end - wall_start
                
                if wall_height > 0:
                    # Scale wall texture column
                    wall_column = pygame.transform.scale(
                        wall_texture.subsurface(texture_x, 0, 1, TEXTURE_HEIGHT),
                        (PROJECTION_SCALE, wall_height)
                    )
                    
                    # Apply distance-based shading with corrected depth
                    shade_factor = max(0.3, 1.0 - (corrected_depth / MAX_DEPTH))
                    wall_column.fill((255, 255, 255, int(255 * shade_factor)), special_flags=pygame.BLEND_RGBA_MULT)
                    
                    surface.blit(wall_column, (ray * PROJECTION_SCALE, wall_start))

                # Draw ceiling above the wall
                draw_ceiling(surface, ray, wall_start, position, current_angle, angle)
                
                # Draw floor below the wall
                draw_floor(surface, ray, wall_end, position, current_angle, angle)
                wall_hit = True
                break

        # If no wall hit, draw ceiling and floor for the entire column
        if not wall_hit:
            draw_ceiling(surface, ray, HALF_SCREEN_HEIGHT, position, current_angle, angle)
            draw_floor(surface, ray, HALF_SCREEN_HEIGHT, position, current_angle, angle)

        current_angle += RAYS_DELTA_ANGLE

def draw_ceiling(surface, ray_index, wall_top, player_pos, ray_angle, player_angle):
    ceiling_texture = texture_manager.get_texture('ceiling')
    
    for y in range(0, wall_top):
        if y == HALF_SCREEN_HEIGHT:
            continue

        diff = HALF_SCREEN_HEIGHT - y
        if diff == 0:
            continue

        distance_to_point = (HALF_SCREEN_HEIGHT * TILE_SIZE) / abs(diff)
        cos_correction = math.cos(ray_angle - player_angle)
        corrected_distance = max(abs(distance_to_point * cos_correction), 1)

        world_x = player_pos[0] + distance_to_point * math.cos(ray_angle)
        world_y = player_pos[1] + distance_to_point * math.sin(ray_angle)

        local_x = math.fmod(world_x, TILE_SIZE)
        local_y = math.fmod(world_y, TILE_SIZE)
        if local_x < 0:
            local_x += TILE_SIZE
        if local_y < 0:
            local_y += TILE_SIZE

        tex_x = int(local_x / TILE_SIZE * TEXTURE_WIDTH)
        tex_y = int(local_y / TILE_SIZE * TEXTURE_HEIGHT)
        
        # Get pixel from ceiling texture
        try:
            ceiling_color = ceiling_texture.get_at((tex_x, tex_y))
        except (IndexError, ValueError):
            ceiling_color = (50, 50, 50)
        
        # Apply distance-based shading
        shade = max(0.1, 0.8 - (corrected_distance * 0.002))
        shaded_color = (
            int(ceiling_color[0] * shade),
            int(ceiling_color[1] * shade),
            int(ceiling_color[2] * shade)
        )
        
        # Draw ceiling pixel
        pygame.draw.rect(surface, shaded_color, 
                        (ray_index * PROJECTION_SCALE, y, PROJECTION_SCALE, 1))

def draw_floor(surface, ray_index, wall_bottom, player_pos, ray_angle, player_angle):
    floor_texture = texture_manager.get_texture('floor')
    
    for y in range(wall_bottom, SCREEN_HEIGHT):
        if y == HALF_SCREEN_HEIGHT:
            continue

        diff = y - HALF_SCREEN_HEIGHT
        if diff == 0:
            continue

        distance_to_point = (HALF_SCREEN_HEIGHT * TILE_SIZE) / abs(diff)
        cos_correction = math.cos(ray_angle - player_angle)
        corrected_distance = max(abs(distance_to_point * cos_correction), 1)

        world_x = player_pos[0] + distance_to_point * math.cos(ray_angle)
        world_y = player_pos[1] + distance_to_point * math.sin(ray_angle)

        local_x = math.fmod(world_x, TILE_SIZE)
        local_y = math.fmod(world_y, TILE_SIZE)
        if local_x < 0:
            local_x += TILE_SIZE
        if local_y < 0:
            local_y += TILE_SIZE

        tex_x = int(local_x / TILE_SIZE * TEXTURE_WIDTH)
        tex_y = int(local_y / TILE_SIZE * TEXTURE_HEIGHT)
        
        # Get pixel from floor texture
        try:
            floor_color = floor_texture.get_at((tex_x, tex_y))
        except (IndexError, ValueError):
            floor_color = (100, 100, 100)
        
        # Apply distance-based shading
        shade = max(0.2, 1.0 - (corrected_distance * 0.002))
        shaded_color = (
            int(floor_color[0] * shade),
            int(floor_color[1] * shade),
            int(floor_color[2] * shade)
        )
        
        # Draw floor pixel
        pygame.draw.rect(surface, shaded_color, 
                        (ray_index * PROJECTION_SCALE, y, PROJECTION_SCALE, 1))