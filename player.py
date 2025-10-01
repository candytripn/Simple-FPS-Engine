import pygame
import math
from configs.config_main import *
from environment.map import world_map

class Player:
    
    def __init__(self):
        # Start at center of grid cell
        self.grid_x = 6  # Grid coordinates
        self.grid_y = 3
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        
        self.direction = 0  # 0=North, 1=East, 2=South, 3=West
        self.angle = DIRECTIONS[self.direction]
        
        # Movement timing
        self.last_move_time = 0
        self.last_turn_time = 0
        
        # Key press tracking to prevent holding keys
        self.keys_pressed = set()

    @property
    def position(self):
        return (self.x, self.y)

    def update_movement(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Track which keys are newly pressed (not held)
        current_keys = set()
        if keys[pygame.K_w]: current_keys.add('w')
        if keys[pygame.K_s]: current_keys.add('s')
        if keys[pygame.K_a]: current_keys.add('a')
        if keys[pygame.K_d]: current_keys.add('d')
        if keys[pygame.K_LEFT]: current_keys.add('left')
        if keys[pygame.K_RIGHT]: current_keys.add('right')
        
        newly_pressed = current_keys - self.keys_pressed
        self.keys_pressed = current_keys
        
        # Movement (only on new key press and after cooldown)
        if current_time - self.last_move_time > MOVE_COOLDOWN:
            if 'w' in newly_pressed:
                self.try_move_forward()
                self.last_move_time = current_time
            elif 's' in newly_pressed:
                self.try_move_backward()
                self.last_move_time = current_time
            elif 'a' in newly_pressed:
                self.try_strafe_left()
                self.last_move_time = current_time
            elif 'd' in newly_pressed:
                self.try_strafe_right()
                self.last_move_time = current_time
        
        # Rotation (only on new key press and after cooldown)
        if current_time - self.last_turn_time > TURN_COOLDOWN:
            if 'left' in newly_pressed:
                self.turn_left()
                self.last_turn_time = current_time
            elif 'right' in newly_pressed:
                self.turn_right()
                self.last_turn_time = current_time

    def try_move_forward(self):
        new_grid_x, new_grid_y = self.get_forward_position()
        if self.is_valid_position(new_grid_x, new_grid_y):
            self.move_to_grid(new_grid_x, new_grid_y)

    def try_move_backward(self):
        new_grid_x, new_grid_y = self.get_backward_position()
        if self.is_valid_position(new_grid_x, new_grid_y):
            self.move_to_grid(new_grid_x, new_grid_y)

    def try_strafe_left(self):
        new_grid_x, new_grid_y = self.get_left_position()
        if self.is_valid_position(new_grid_x, new_grid_y):
            self.move_to_grid(new_grid_x, new_grid_y)

    def try_strafe_right(self):
        new_grid_x, new_grid_y = self.get_right_position()
        if self.is_valid_position(new_grid_x, new_grid_y):
            self.move_to_grid(new_grid_x, new_grid_y)

    def get_forward_position(self):
        if self.direction == 0:    # North
            return self.grid_x, self.grid_y - 1
        elif self.direction == 1:  # East
            return self.grid_x + 1, self.grid_y
        elif self.direction == 2:  # South
            return self.grid_x, self.grid_y + 1
        else:  # West
            return self.grid_x - 1, self.grid_y

    def get_backward_position(self):
        if self.direction == 0:    # North
            return self.grid_x, self.grid_y + 1
        elif self.direction == 1:  # East
            return self.grid_x - 1, self.grid_y
        elif self.direction == 2:  # South
            return self.grid_x, self.grid_y - 1
        else:  # West
            return self.grid_x + 1, self.grid_y

    def get_left_position(self):
        if self.direction == 0:    # North
            return self.grid_x - 1, self.grid_y
        elif self.direction == 1:  # East
            return self.grid_x, self.grid_y - 1
        elif self.direction == 2:  # South
            return self.grid_x + 1, self.grid_y
        else:  # West
            return self.grid_x, self.grid_y + 1

    def get_right_position(self):
        if self.direction == 0:    # North
            return self.grid_x + 1, self.grid_y
        elif self.direction == 1:  # East
            return self.grid_x, self.grid_y + 1
        elif self.direction == 2:  # South
            return self.grid_x - 1, self.grid_y
        else:  # West
            return self.grid_x, self.grid_y - 1

    def is_valid_position(self, grid_x, grid_y):
        # Check if position is within bounds and not a wall
        world_x = grid_x * GRID_SIZE
        world_y = grid_y * GRID_SIZE
        return (world_x, world_y) not in world_map

    def move_to_grid(self, new_grid_x, new_grid_y):
        self.grid_x = new_grid_x
        self.grid_y = new_grid_y
        # Center player in the grid cell
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2

    def turn_left(self):
        self.direction = (self.direction - 1) % 4
        self.angle = DIRECTIONS[self.direction]

    def turn_right(self):
        self.direction = (self.direction + 1) % 4
        self.angle = DIRECTIONS[self.direction]

