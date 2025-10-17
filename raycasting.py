import math
import pygame
from configs.config_main import *
from colors import *
from textures import texture_manager

def cast_rays_sector(surface, position, angle, rays_count, current_world_map, sprites=None, ceiling_correction_factor=1.0, angle_correction_power=1.0):
    current_angle = angle - HALF_FOV
    xo, yo = position

    # Store depth buffer for sprite rendering
    depth_buffer = []

    floor_texture = texture_manager.get_texture('floor')
    ceiling_texture = texture_manager.get_texture('ceiling')

    for ray in range(rays_count):
        sin_a = math.sin(current_angle)
        cos_a = math.cos(current_angle)

        wall_hit = False
        wall_depth = MAX_DEPTH
        
        for depth in range(0, MAX_DEPTH, 1):
            x = xo + depth * cos_a
            y = yo + depth * sin_a

            # Use the passed world_map parameter instead of imported one
            target_tile = (x // TILE_SIZE * TILE_SIZE, y // TILE_SIZE * TILE_SIZE)
            if target_tile in current_world_map:  # Use current_world_map here
                wall_depth = depth
                # FISH-EYE CORRECTION: Apply cosine correction to remove distortion
                corrected_depth = depth * math.cos(current_angle - angle)
                
                # Prevent division by zero or negative values
                if corrected_depth <= 0:
                    corrected_depth = 1

                projection_height = PROJECTION_COEF / corrected_depth
                
                # Calculate texture coordinate for wall
                # Determine which wall face we hit and get proper texture coordinates
                hit_x = x % TILE_SIZE
                hit_y = y % TILE_SIZE
                
                # Determine wall orientation and get texture X coordinate
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                # Get the appropriate wall texture for this tile position
                wall_texture = texture_manager.get_wall_texture(tile_x, tile_y)
                
                # Check if we hit a vertical or horizontal wall
                # by checking which edge of the tile we're closest to
                dist_to_left = hit_x
                dist_to_right = TILE_SIZE - hit_x
                dist_to_top = hit_y
                dist_to_bottom = TILE_SIZE - hit_y
                
                min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)
                
                if min_dist == dist_to_left or min_dist == dist_to_right:
                    # Hit vertical wall - use Y coordinate for texture
                    texture_x = int((hit_y / TILE_SIZE) * TEXTURE_WIDTH) % TEXTURE_WIDTH
                else:
                    # Hit horizontal wall - use X coordinate for texture
                    texture_x = int((hit_x / TILE_SIZE) * TEXTURE_WIDTH) % TEXTURE_WIDTH
                
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
                    # Draw the wall column by sampling from the texture
                    for y_pixel in range(wall_height):
                        screen_y = wall_start + y_pixel
                        if 0 <= screen_y < SCREEN_HEIGHT:
                            # Calculate which Y coordinate in the texture to sample
                            texture_y = int((y_pixel / wall_height) * TEXTURE_HEIGHT) % TEXTURE_HEIGHT
                            texture_y = max(0, min(TEXTURE_HEIGHT - 1, texture_y))
                            
                            # Get the color from the wall texture
                            try:
                                wall_color = wall_texture.get_at((texture_x, texture_y))
                            except (IndexError, ValueError):
                                wall_color = (128, 128, 128)  # Fallback gray
                            
                            # Apply distance-based shading
                            shade_factor = max(0.3, 1.0 - (corrected_depth / MAX_DEPTH))
                            shaded_color = (
                                int(wall_color[0] * shade_factor),
                                int(wall_color[1] * shade_factor),
                                int(wall_color[2] * shade_factor)
                            )
                            
                            # Draw the pixel
                            pygame.draw.rect(surface, shaded_color, 
                                           (ray * PROJECTION_SCALE, screen_y, PROJECTION_SCALE, 1))

                # Draw ceiling above the wall - pass the correction parameters
                draw_ceiling(surface, ray, wall_start, position, current_angle, angle, ceiling_correction_factor, angle_correction_power)
                
                # Draw floor below the wall
                draw_floor(surface, ray, wall_end, position, current_angle, angle)
                wall_hit = True
                break

        # If no wall hit, draw ceiling and floor for the entire column
        if not wall_hit:
            draw_ceiling(surface, ray, HALF_SCREEN_HEIGHT, position, current_angle, angle, ceiling_correction_factor, angle_correction_power)
            draw_floor(surface, ray, HALF_SCREEN_HEIGHT, position, current_angle, angle)

        # Store depth for this ray
        depth_buffer.append(wall_depth)
        current_angle += RAYS_DELTA_ANGLE

    # Render sprites after walls
    if sprites:
        render_sprites(surface, position, angle, sprites, depth_buffer)

def render_sprites(surface, player_pos, player_angle, sprites, depth_buffer):
    """Render all sprites based on distance and angle from player"""
    sprite_projections = []
    
    for sprite in sprites:
        # Convert sprite grid position to world position (center of tile)
        sprite_world_x = (sprite.x * TILE_SIZE) + (TILE_SIZE // 2)
        sprite_world_y = (sprite.y * TILE_SIZE) + (TILE_SIZE // 2)
        
        # Calculate distance from player to sprite
        dx = sprite_world_x - player_pos[0]
        dy = sprite_world_y - player_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:  # Avoid division by zero
            distance = 1
        
        # Calculate angle from player to sprite
        sprite_angle = math.atan2(dy, dx)
        
        # Calculate relative angle (sprite angle relative to player's view direction)
        angle_diff = sprite_angle - player_angle
        
        # Normalize angle difference to [-π, π]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Check if sprite is within field of view
        if abs(angle_diff) < HALF_FOV + 0.5:  # Add small buffer
            # Calculate screen x position
            screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
            
            # Calculate sprite size based on distance
            sprite_size = int(PROJECTION_COEF / distance)
            
            # Store sprite projection info
            sprite_projections.append({
                'sprite': sprite,
                'distance': distance,
                'screen_x': screen_x,
                'size': sprite_size,
                'angle_diff': angle_diff
            })
    
    # Sort sprites by distance (farthest first for proper depth)
    sprite_projections.sort(key=lambda x: x['distance'], reverse=True)
    
    # Render each sprite
    for proj in sprite_projections:
        draw_sprite(surface, proj, depth_buffer)

def draw_sprite(surface, sprite_proj, depth_buffer):
    """Draw a single sprite on the screen"""
    sprite = sprite_proj['sprite']
    screen_x = sprite_proj['screen_x']
    distance = sprite_proj['distance']
    
    # Get current sprite frame
    sprite_image = sprite.get_current_sprite()
    
    if sprite_image is None:
        return
    
    # Calculate base sprite size based on distance
    base_sprite_size = int(PROJECTION_COEF / distance)
    
    # Use the sprite's individual scale factor
    actual_sprite_size = max(1, int(base_sprite_size * sprite.scale_factor))
    
    # Calculate sprite screen position and dimensions
    sprite_screen_x = int(screen_x - actual_sprite_size // 2)
    sprite_screen_y = int(HALF_SCREEN_HEIGHT - actual_sprite_size // 2)
    
    # Scale the sprite image to the calculated size
    if actual_sprite_size > 0:
        try:
            scaled_sprite = pygame.transform.scale(sprite_image, (actual_sprite_size, actual_sprite_size))
            
            # Draw sprite pixel by pixel with depth checking
            for x in range(actual_sprite_size):
                screen_col = sprite_screen_x + x
                
                # Check if within screen bounds
                if 0 <= screen_col < SCREEN_WIDTH:
                    # Convert screen column to ray index for depth checking
                    ray_index = screen_col // PROJECTION_SCALE
                    
                    if 0 <= ray_index < len(depth_buffer):
                        # Only draw if sprite is closer than the wall at this column
                        if distance < depth_buffer[ray_index]:
                            for y in range(actual_sprite_size):
                                screen_row = sprite_screen_y + y
                                
                                if 0 <= screen_row < SCREEN_HEIGHT:
                                    # Get pixel color from scaled sprite
                                    try:
                                        pixel_color = scaled_sprite.get_at((x, y))
                                        
                                        # Check for transparency (assuming black is transparent)
                                        if pixel_color[3] > 0:  # Alpha channel check
                                            # Apply distance shading
                                            shade_factor = max(0.3, 1.0 - (distance / MAX_DEPTH))
                                            shaded_color = (
                                                int(pixel_color[0] * shade_factor),
                                                int(pixel_color[1] * shade_factor),
                                                int(pixel_color[2] * shade_factor)
                                            )
                                            
                                            surface.set_at((screen_col, screen_row), shaded_color)
                                    except (IndexError, ValueError):
                                        pass  # Skip invalid pixels
        except (ValueError, pygame.error):
            pass  # Skip if scaling fails

def draw_ceiling(surface, ray_index, wall_top, player_pos, ray_angle, player_angle, ceiling_correction_factor=1.0, angle_correction_power=1.0):
    ceiling_texture = texture_manager.get_texture('ceiling')
    
    # Debug removed - ceiling function working correctly
    
    for y in range(0, wall_top):
        if y == HALF_SCREEN_HEIGHT:
            continue

        diff = HALF_SCREEN_HEIGHT - y
        if diff == 0:
            continue

        # formula off!!!
        distance_to_point = (HALF_SCREEN_HEIGHT * TILE_SIZE) / abs(diff)
        
        # fisheye correction with adjustable power
        base_correction = math.cos(ray_angle - player_angle)
        enhanced_correction = math.pow(abs(base_correction), angle_correction_power) * (1 if base_correction >= 0 else -1)
        corrected_distance = max(abs(distance_to_point * enhanced_correction * ceiling_correction_factor), 1)

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
        
        # Clamp texture coordinates to valid range
        tex_x = max(0, min(TEXTURE_WIDTH - 1, tex_x))
        tex_y = max(0, min(TEXTURE_HEIGHT - 1, tex_y))
        
        # Get pixel from ceiling texture
        try:
            ceiling_color = ceiling_texture.get_at((tex_x, tex_y))
        except (IndexError, ValueError):
            ceiling_color = (50, 50, 50)  # Fallback color
        
        # Use the actual ceiling texture with minimal shading
        shade = max(0.7, 1.0 - (corrected_distance * 0.0003))  # Very bright shading
        shaded_color = (
            int(ceiling_color[0] * shade),
            int(ceiling_color[1] * shade),
            int(ceiling_color[2] * shade)
        )
        
        # Ceiling texture rendering working perfectly!
        
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