from configs.config_main import *

# Define multiple text maps
dungeon_level_1 = [
    "WWWWWWWWWWWW",
    "W...W......W",
    "W...W......W",
    "W..........W",
    "W..........W",
    "W...WWW..WWW",
    "W...W......W",
    "WWWWWWWWWWWW",
]

combat_arena = [
    "WWWW",
    "W..W",
    "WWWW",
]

boss_room = [
    "WWWWWWWWWWWWWWWW",
    "W..............W",
    "W..............W",
    "W......B.......W",
    "W..............W",
    "W..............W",
    "WWWWWWWWWWWWWWWW",
]

def create_world_map(text_map):
    """Convert text map to world_map set"""
    world_map = set()
    for j, row in enumerate(text_map):
        for i, char in enumerate(row):
            if char == "W":
                wall_position = (i * TILE_SIZE, j * TILE_SIZE)
                world_map.add(wall_position)
    return world_map

# Create different world maps
world_maps = {
    "dungeon_level_1": create_world_map(dungeon_level_1),
    "combat_arena": create_world_map(combat_arena),
    "boss_room": create_world_map(boss_room),
}

# Default current map
current_map_name = "dungeon_level_1"
world_map = world_maps[current_map_name]

def switch_map(map_name):
    """Switch to a different map"""
    global world_map, current_map_name
    if map_name in world_maps:
        world_map = world_maps[map_name]
        current_map_name = map_name
        print(f"Switched to map: {map_name}")
    else:
        print(f"Map '{map_name}' not found!")

def get_current_map():
    return current_map_name