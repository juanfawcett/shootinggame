"""
Configuración del juego Panda3D Shooting Game
"""

# Game timings and speeds
GAME_DURATION = 60.0          # seconds to survive
SHOT_INTERVAL = 0.5          # seconds between shots
ENEMY_SPAWN_INTERVAL = 1.0    # seconds between enemy spawns
PLAYER_SPEED = 12.0           # player movement speed (units/sec)
SHOT_SPEED = 30.0             # shot movement speed (units/sec)
EXPLOSION_DURATION = 0.5      # Explosion display duration in seconds
EXPLOSION_SPEED = 5.0         # Explosion movement speed (units/sec)
BONUS_SPAWN_INTERVAL = 10.0   # seconds between bonus spawns

# Screen shake parameters
SHAKE_INTENSITY = 0.5         # Maximum offset for screen shake
SHAKE_DURATION = 0.4          # Duration of the screen shake in seconds

# Red filter parameters
RED_FILTER_INTENSITY = 0.4    # Alpha value of the red filter (0.0 to 1.0)
RED_FILTER_DURATION = 0.3     # Duration of the red filter in seconds

# Screen / game area bounds and positions
LEFT_BOUND = -3.5             # left-most x position for the player
RIGHT_BOUND = 3.5             # right-most x position for the player
PLAYER_START_X = 0.0          # initial player x position
PLAYER_START_Y = -10.0        # fixed player y position (bottom of play area)
ENEMY_SPAWN_Y = 26.0          # y position where enemies appear

# Calculate bonus spawn positions
TOTAL_WIDTH = RIGHT_BOUND - LEFT_BOUND
BONUS_SPAWN_POSITIONS = [
    LEFT_BOUND + (TOTAL_WIDTH * 0.25),   # First quarter
    LEFT_BOUND + (TOTAL_WIDTH * 0.75)    # Third quarter
]

# Camera settings (third-person view)
CAMERA_DISTANCE = 10.0        # Distance behind the player
CAMERA_HEIGHT = 10.0          # Height above the player
CAMERA_LOOK_AT_OFFSET = 10.0  # Look slightly ahead of the player

# Scales for sprites
PLAYER_SCALE = 2.0            # scale for the player sprite
SHOT_SCALE = 0.6              # scale for the shot sprite
EXPLOSION_SCALE = 0.5         # scale for the explosion sprite
EXPLOSION_SCALE_MULTIPLIER = 1.1  # Multiplier for explosion scale relative to enemy scale
BONUS_SCALE = 5.0             # scale for the bonus sprite

# Bonus parameters
BONUS_STARTING_VALUE = -5     # starting value for bonus
BONUS_MAX_VALUE = 10          # maximum value for bonus
BONUS_MIN_VALUE = BONUS_STARTING_VALUE         # minimum value for bonus
BONUS_SPEED = 3.0             # bonus movement speed (units/sec)
BONUS_TRANSPARENCY = 0.6      # transparency value for bonuses (0.0=fully transparent, 1.0=fully opaque)

# Window configuration parameters
WINDOW_WIDTH = 450            # Width of the game window
WINDOW_HEIGHT = 750           # Height of the game window
WINDOW_TITLE = "Panda3D Shooting Game"  # Title of the game window

# Asset file paths
CHARACTER_IDLE_IMAGE = "assets/character_idle.png"
CHARACTER_LEFT_IMAGE = "assets/character_left.png"
CHARACTER_RIGHT_IMAGE = "assets/character_right.png"
SHOT_IMAGE = "assets/shot.png"
EXPLOSION_IMAGE = "assets/explosion.png"
BONUS_POSITIVE_IMAGE = "assets/bonus_positive.png"
BONUS_NEGATIVE_IMAGE = "assets/bonus_negative.png"
BACKGROUND_IMAGE = "assets/background.png"

# Background parameters
BACKGROUND_POS_X = 0.0        # X offset for the background
BACKGROUND_POS_Y = -3.0       # Y offset for the background
BACKGROUND_SCALE = 12

# Enemy types configuration
ENEMY_TYPES = {
    1: {"hp": 1,  "speed": 15.0 / 4, "scale": 1.0, "image": "assets/enemy2.png"},
    2: {"hp": 2,  "speed": 12.0 / 4, "scale": 1.2, "image": "assets/enemy2.png"},
    3: {"hp": 6,  "speed": 9.0 / 5,  "scale": 1.4, "image": "assets/enemy3.png"},
    4: {"hp": 8, "speed": 6.0 / 5,  "scale": 1.7, "image": "assets/enemy.png"},
}

# Enemy spawn probabilities (45%, 25%, 20%, 10%)
ENEMY_SPAWN_PROB = [0.45, 0.25, 0.20, 0.10]

# Player configuration
PLAYER_STARTING_LIFE = 3
