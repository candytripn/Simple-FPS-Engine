import pygame
import os
from configs.config_main import *

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.loaded = False
    
    def load_textures(self):
        if self.loaded:
            return
            
        # Load actual image files from textures folder
        texture_path = "textures"
        
        try:
            # Load wall texture from PNG file
            wall_texture_path = os.path.join(texture_path, "Brick_Wall_64x64.png")
            if os.path.exists(wall_texture_path):
                wall_texture = pygame.image.load(wall_texture_path).convert_alpha()
                # Scale to our texture size if needed
                wall_texture = pygame.transform.scale(wall_texture, (TEXTURE_WIDTH, TEXTURE_HEIGHT))
                self.textures['wall'] = wall_texture
            else:
                # Fallback to procedural texture if file not found
                print(f"Warning: {wall_texture_path} not found, using procedural texture")
                self.create_procedural_wall_texture()
        except pygame.error as e:
            print(f"Error loading wall texture: {e}")
            self.create_procedural_wall_texture()
        
        # Load floor texture 
        try:
            floor_texture_path = os.path.join(texture_path, "Dirt_Road_64x64.png")
            if os.path.exists(floor_texture_path):
                floor_texture = pygame.image.load(floor_texture_path).convert_alpha()
                floor_texture = pygame.transform.scale(floor_texture, (TEXTURE_WIDTH, TEXTURE_HEIGHT))
                self.textures['floor'] = floor_texture
            else:
                self.create_procedural_floor_texture()
        except pygame.error as e:
            print(f"Error loading floor texture: {e}")
            self.create_procedural_floor_texture()
        
        # Load ceiling texture
            ceiling_texture_path = os.path.join(texture_path, "Dirty_Mossy_Tiles_64x64.png")
            if os.path.exists(ceiling_texture_path):
                ceiling_texture = pygame.image.load(ceiling_texture_path).convert_alpha()
                ceiling_texture = pygame.transform.scale(ceiling_texture, (TEXTURE_WIDTH, TEXTURE_HEIGHT))
                # Make ceiling darker
                ceiling_texture.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
                self.textures['ceiling'] = ceiling_texture
            else:
                self.create_procedural_ceiling_texture()
        except pygame.error as e:
            print(f"Error loading ceiling texture: {e}")
            self.create_procedural_ceiling_texture()
        
        self.loaded = True
    
    def create_procedural_wall_texture(self):
        """Fallback procedural wall texture"""
        wall_texture = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        for y in range(TEXTURE_HEIGHT):
            color = 100 + (y * 155 // TEXTURE_HEIGHT)
            wall_texture.fill((color, color // 2, color // 4), (0, y, TEXTURE_WIDTH, 1))
        self.textures['wall'] = wall_texture
    
    def create_procedural_floor_texture(self):
        """Fallback procedural floor texture"""
        floor_texture = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        for y in range(TEXTURE_HEIGHT):
            for x in range(TEXTURE_WIDTH):
                checker = ((x // 8) + (y // 8)) % 2
                color = 80 if checker else 60
                floor_texture.set_at((x, y), (color, color, color))
        self.textures['floor'] = floor_texture
    
    def create_procedural_ceiling_texture(self):
        """Fallback procedural ceiling texture"""
        ceiling_texture = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        for y in range(TEXTURE_HEIGHT):
            for x in range(TEXTURE_WIDTH):
                checker = ((x // 6) + (y // 6)) % 2
                color = 40 if checker else 30
                ceiling_texture.set_at((x, y), (color, color, color + 10))
        self.textures['ceiling'] = ceiling_texture
    
    def get_texture(self, name):
        # Load textures on first access if not already loaded
        if not self.loaded:
            self.load_textures()
        return self.textures.get(name)

# Global texture manager instance
texture_manager = TextureManager()