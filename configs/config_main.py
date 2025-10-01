import math

# game
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2

TARGET_FPS = 60

TILE_SIZE = 100

# ray casting
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUMBER_OF_RAYS = 120
RAYS_DELTA_ANGLE = FOV / NUMBER_OF_RAYS
MAX_DEPTH = 800

PROJECTION_DISTANCE = NUMBER_OF_RAYS / (2 * math.tan(HALF_FOV))
PROJECTION_COEF = 6 * PROJECTION_DISTANCE * TILE_SIZE
PROJECTION_SCALE = SCREEN_WIDTH // NUMBER_OF_RAYS

# texture settings
TEXTURE_WIDTH = 64
TEXTURE_HEIGHT = 64

# grid-based movement settings
GRID_SIZE = TILE_SIZE
MOVE_COOLDOWN = 200  # milliseconds between moves
TURN_COOLDOWN = 150  # milliseconds between turns

# Cardinal directions (0=North, 1=East, 2=South, 3=West)
# In pygame: Y increases downward, angles measured clockwise from positive X (East)
DIRECTIONS = [
    -math.pi / 2,    # North (270 degrees, negative Y direction)
    0,               # East (0 degrees, positive X direction)  
    math.pi / 2,     # South (90 degrees, positive Y direction)
    math.pi          # West (180 degrees, negative X direction)
]

# temp player - start in center of a grid cell
player_position = (GRID_SIZE * 6 + GRID_SIZE // 2, GRID_SIZE * 3 + GRID_SIZE // 2)  # Center of grid cell
player_angle = 0
player_speed = 2

# In configs/config_main.py
FLOOR_TEXTURE_SCALE = 64
CEILING_TEXTURE_SCALE = 64