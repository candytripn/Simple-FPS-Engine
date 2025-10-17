import pygame

class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as message:
            print(f'Unable to load spritesheet image: {filename}')
            raise SystemExit(message)
    
    def image_at(self, rectangle, colorkey=None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    
    def images_at(self, rects, colorkey=None):
        """Loads multiple images, supply a list of coordinates""" 
        return [self.image_at(rect, colorkey) for rect in rects]
    
    def load_strip(self, rect, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list"""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class Sprite:
    """Base sprite class"""
    def __init__(self, x, y, sprite_sheet, animation_frames, scale_factor=1.0, sprite_type="generic"):
        self.x = x
        self.y = y
        self.sprite_sheet = sprite_sheet
        self.animation_frames = animation_frames
        self.current_frame = 0
        self.animation_speed = 200  # milliseconds per frame
        self.last_update = pygame.time.get_ticks()
        self.scale_factor = scale_factor
        self.sprite_type = sprite_type
        
        # Sprite stats
        self.health = 100
        self.max_health = 100
        self.is_alive = True
    
    @property
    def position(self):
        return (self.x, self.y)
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
    
    def get_current_sprite(self):
        return self.animation_frames[self.current_frame]
    
    def take_damage(self, damage):
        """Apply damage to sprite"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
    
    def move_to(self, new_x, new_y):
        """Move sprite to new grid position"""
        self.x = new_x
        self.y = new_y

class Enemy(Sprite):
    """Enemy sprite subclass"""
    def __init__(self, x, y, sprite_sheet, animation_frames, scale_factor=1.0, enemy_type="demon"):
        super().__init__(x, y, sprite_sheet, animation_frames, scale_factor, "enemy")
        self.enemy_type = enemy_type
        self.damage = 10
        self.experience_value = 50
        
        # Set stats based on enemy type
        if enemy_type == "demon":
            self.health = 75
            self.max_health = 75
            self.damage = 15
            self.experience_value = 100
        elif enemy_type == "skeleton":
            self.health = 50
            self.max_health = 50
            self.damage = 8
            self.experience_value = 25
    
    def attack_player(self, player):
        """Attack the player"""
        if self.is_alive:
            print(f"{self.enemy_type} attacks for {self.damage} damage!")
            return self.damage
        return 0
    
    def on_death(self):
        """Called when enemy dies"""
        print(f"{self.enemy_type} has been defeated! Gained {self.experience_value} XP")
        return self.experience_value

class Boss(Enemy):
    """Boss enemy subclass"""
    def __init__(self, x, y, sprite_sheet, animation_frames, scale_factor=1.0, boss_type="demon_lord"):
        super().__init__(x, y, sprite_sheet, animation_frames, scale_factor, boss_type)
        self.sprite_type = "boss"
        
        # Boss stats are much higher
        if boss_type == "demon_lord":
            self.health = 300
            self.max_health = 300
            self.damage = 35
            self.experience_value = 500
        
        self.special_attacks = ["fireball", "summon_minions"]
    
    def special_attack(self, attack_type):
        """Perform special boss attack"""
        if attack_type == "fireball":
            print(f"{self.enemy_type} casts Fireball!")
            return self.damage * 2
        elif attack_type == "summon_minions":
            print(f"{self.enemy_type} summons minions!")
            return 0
        return self.damage

pygame.init()
pygame.display.set_mode((1, 1))  # Initialize display mode

# Update this path based on the actual file location
sprite_sheet = SpriteSheet('C:\\intro to programming\\Simple-FPS-Engine\\Flying Demon 2D Pixel Art\\Sprites\\with_outline\\IDLE.png')

walk_animation = sprite_sheet.load_strip((0, 0, 32, 32), 4)
current_frame = 0
frame_delay = 100  # milliseconds
last_update = pygame.time.get_ticks()
