import pygame
import os
from configs.config_main import *

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.wall_textures = []  # List of wall texture variations
        self.loaded = False
    
    def load_textures(self):
        if self.loaded:
            return
            
        # Load actual image files from textures folder
        texture_path = "textures"
        
        # Load multiple wall texture variations
        wall_texture_files = [
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\04.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\05.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\06.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\07.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\08.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\09.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\10.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\11.jpg",
"C:\\intro to programming\\Simple-FPS-Engine\\textures\\12.jpg",
        ]
        
        loaded_wall_textures = []
        for texture_file in wall_texture_files:
            try:
                wall_texture_path = os.path.join(texture_path, texture_file)
                if os.path.exists(wall_texture_path):
                    wall_texture = pygame.image.load(wall_texture_path).convert_alpha()
                    wall_texture = pygame.transform.scale(wall_texture, (TEXTURE_WIDTH, TEXTURE_HEIGHT))
                    loaded_wall_textures.append(wall_texture)
                    print(f"✓ Loaded wall texture: {texture_file}")
                else:
                    print(f"Warning: {texture_file} not found")
            except pygame.error as e:
                print(f"Error loading {texture_file}: {e}")
        
        if loaded_wall_textures:
            self.wall_textures = loaded_wall_textures
            # Keep the first texture as the default 'wall' texture for backward compatibility
            self.textures['wall'] = loaded_wall_textures[0]
            print(f"✓ Loaded {len(loaded_wall_textures)} wall texture variations")
        else:
            print("No wall textures loaded, creating procedural texture")
            self.create_procedural_wall_texture()
        
        # Load floor texture 
        try:
            floor_texture_path = os.path.join(texture_path, "C:\\intro to programming\\Simple-FPS-Engine\\textures\\Wooden_Floor_Horizontal_64x64.png")
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
        try:
            ceiling_texture_path = os.path.join(texture_path, "C:\\intro to programming\\Simple-FPS-Engine\\textures\\Rocky_Road_64x64.png")
            if os.path.exists(ceiling_texture_path):
                ceiling_texture = pygame.image.load(ceiling_texture_path).convert_alpha()
                ceiling_texture = pygame.transform.scale(ceiling_texture, (TEXTURE_WIDTH, TEXTURE_HEIGHT))
                self.textures['ceiling'] = ceiling_texture
                print(f'✓ Loaded ceiling texture: {ceiling_texture_path}')
            else:
                print(f"Warning: {ceiling_texture_path} not found, using procedural texture")
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
        print("=" * 50)
        print("WARNING: CREATING PROCEDURAL CEILING TEXTURE!")
        print("This means the real texture failed to load or was overwritten!")
        print("=" * 50)
        
        # Create a very obvious bright red texture instead of checkerboard
        ceiling_texture = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
        ceiling_texture.fill((255, 0, 0))  # Solid bright red
        
        self.textures['ceiling'] = ceiling_texture
        print("BRIGHT RED PROCEDURAL CEILING TEXTURE CREATED!")
        print("=" * 50)
    
    def get_texture(self, name):
        # Load textures on first access if not already loaded
        if not self.loaded:
            self.load_textures()
    
        texture = self.textures.get(name)
        if texture is None:
            print(f"ERROR: Texture '{name}' not found! Available: {list(self.textures.keys())}")
            # Return a debug texture so we can see something
            debug_texture = pygame.Surface((TEXTURE_WIDTH, TEXTURE_HEIGHT))
            debug_texture.fill((255, 0, 0))  # Red for missing textures
            return debug_texture
    
        return texture
    
    def get_wall_texture(self, tile_x, tile_y):
        """Get wall texture based on tile position - creates variety and makes movement visible"""
        if not self.loaded:
            self.load_textures()
            
        if not self.wall_textures:
            return self.get_texture('wall')
        
        # Create a deterministic but varied pattern based on tile coordinates
        # This ensures the same tile always gets the same texture (consistent)
        # but different tiles get different textures (variety)
        texture_index = (tile_x * 7 + tile_y * 13) % len(self.wall_textures)
        return self.wall_textures[texture_index]

# Global texture manager instance
texture_manager = TextureManager()