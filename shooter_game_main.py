#!/usr/bin/env python3
"""
Panda3D Shooting Game with Third-Person Perspective and Background
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, Vec3, TransparencyAttrib, Point3, loadPrcFileData, TextNode, LVecBase4f
import random
import sys

# ============================
# CONFIGURATION PARAMETERS
# ============================

# Game timings and speeds
GAME_DURATION = 60.0          # seconds to survive
SHOT_INTERVAL = 0.20          # seconds between shots
ENEMY_SPAWN_INTERVAL = 1.0      # seconds between enemy spawns
PLAYER_SPEED = 12.0           # player movement speed (units/sec)
SHOT_SPEED = 30.0             # shot movement speed (units/sec)
EXPLOSION_DURATION = 0.5      # Explosion display duration in seconds
EXPLOSION_SPEED = 5.0         # Explosion movement speed (units/sec)
BONUS_SPAWN_INTERVAL = 15.0    # seconds between bonus spawns

# Screen shake parameters
SHAKE_INTENSITY = 0.5         # Maximum offset for screen shake
SHAKE_DURATION = 0.4          # Duration of the screen shake in seconds

# Red filter parameters
RED_FILTER_INTENSITY = 0.4    # Alpha value of the red filter (0.0 to 1.0)
RED_FILTER_DURATION = 0.3     # Duration of the red filter in seconds

# Screen / game area bounds and positions
LEFT_BOUND = -3.5            # left-most x position for the player
RIGHT_BOUND = 3.5           # right-most x position for the player
PLAYER_START_X = 0.0          # initial player x position
PLAYER_START_Y = -10.0         # fixed player y position (bottom of play area)
ENEMY_SPAWN_Y = 26.0          # y position where enemies appear

# Camera settings (third-person view)
CAMERA_DISTANCE = 10.0        # Distance behind the player
CAMERA_HEIGHT = 10.0          # Height above the player
CAMERA_LOOK_AT_OFFSET = 10.0   # Look slightly ahead of the player

# Scales for sprites
PLAYER_SCALE = 2.0            # scale for the player sprite
SHOT_SCALE = 0.6              # scale for the shot sprite
EXPLOSION_SCALE = 0.5         # scale for the explosion sprite
EXPLOSION_SCALE_MULTIPLIER = 1.1 # Multiplier for explosion scale relative to enemy scale
BONUS_SCALE = 5.0             # scale for the bonus sprite

# Bonus parameters
BONUS_STARTING_VALUE = -10    # starting value for bonus
BONUS_MAX_VALUE = 10          # maximum value for bonus
BONUS_MIN_VALUE = -10          # minimum value for bonus
BONUS_SPEED = 3.0             # bonus movement speed (units/sec)
BONUS_POSITIVE_IMAGE = "assets/bonus_positive.png" # image for positive bonus
BONUS_NEGATIVE_IMAGE = "assets/bonus_negative.png" # image for negative bonus
BONUS_TRANSPARENCY = 0.6      # transparency value for bonuses (0.0=fully transparent, 1.0=fully opaque)

# Window configuration parameters
WINDOW_WIDTH = 450            # Width of the game window
WINDOW_HEIGHT = 750           # Height of the game window
WINDOW_TITLE = "Panda3D Shooting Game" # Title of the game window

# PNG filenames (ensure these files are in your assets folder)
CHARACTER_IMAGE = "assets/character.png"
CHARACTER_IDLE_IMAGE = "assets/character_idle.png" # New idle image
CHARACTER_LEFT_IMAGE = "assets/character_left.png" # New left movement image
CHARACTER_RIGHT_IMAGE = "assets/character_right.png" # New right movement image
SHOT_IMAGE = "assets/shot.png"
EXPLOSION_IMAGE = "assets/explosion.png" # Filename for explosion image

# Background parameters (adjust these to center the background)
BACKGROUND_IMAGE = "assets/background.png"
BACKGROUND_POS_X = 0.0          # X offset for the background
BACKGROUND_POS_Y = -3.0          # Y offset for the background
BACKGROUND_SCALE = 12

# Enemy types: each entry contains hit points, movement speed, sprite scale, and image file
ENEMY_TYPES = {
    1: {"hp": 2,  "speed": 15.0 / 2, "scale": 1.0, "image": "assets/enemy2.png"},
    2: {"hp": 4,  "speed": 12.0 / 2, "scale": 1.2, "image": "assets/enemy2.png"},
    3: {"hp": 8,  "speed": 9.0 / 2,  "scale": 1.4, "image": "assets/enemy3.png"},
    4: {"hp": 16, "speed": 6.0 / 2,  "scale": 1.7, "image": "assets/enemy.png"},
}

# Enemy spawn probabilities (45%, 25%, 20%, 10%)
ENEMY_SPAWN_PROB = [0.45, 0.25, 0.20, 0.10]

# Player starting life
PLAYER_STARTING_LIFE = 3

# ============================
# APPLY WINDOW CONFIGURATION
# ============================
loadPrcFileData("", f"win-size {WINDOW_WIDTH} {WINDOW_HEIGHT}")
loadPrcFileData("", f"window-title {WINDOW_TITLE}")
loadPrcFileData("", "win-fixed-size 1")

# ============================
# GAME CLASS DEFINITION
# ============================

class ShootingGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()  # Disable default mouse camera control

        # Create the background (drawn behind all game objects)
        self.background = self.createBackground()

        # Initialize game state parameters
        self.gameOver = False
        self.gameStartTime = globalClock.getRealTime()
        self.shots = []    # List to hold active shots
        self.enemies = []  # List to hold active enemies
        self.explosions = [] # List to hold active explosions
        self.bonuses = []  # List to hold active bonuses
        self.keyMap = {"left": False, "right": False}
        self.playerLife = PLAYER_STARTING_LIFE

        # Player shot modifiers (affected by bonuses)
        self.currentShotInterval = SHOT_INTERVAL
        self.currentShotScale = SHOT_SCALE

        # New feature: win and stage tracking
        self.winCount = 0      # Counts total wins (games won)
        self.stage = 1         # Current stage (starts at 1)
        self.lastWin = None    # Tracks if the last game ended in a win

        # UI elements (timer, win count, life counter, and game status)
        # Parent texts to fixed aspect2d nodes so that they remain visible regardless of window size.
        self.timerText = OnscreenText(
            text="Time: 0",
            pos=(0.05, -0.08),
            scale=0.08,
            fg=(1,1,1,1),
            align=TextNode.ALeft,
            parent=base.a2dTopLeft
        )
        self.winCountText = OnscreenText(
            text="Wins: 0",
            pos=(-0.05, -0.08),
            scale=0.08,
            fg=(1,1,1,1),
            align=TextNode.ARight,
            parent=base.a2dTopRight
        )
        self.lifeText = OnscreenText(
            text=f"Life: {self.playerLife}",
            pos=(0.05, -0.16),
            scale=0.08,
            fg=(1,1,1,1),
            align=TextNode.ALeft,
            parent=base.a2dTopLeft
        )
        self.statusText = OnscreenText(
            text="",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 0, 0, 1)
        )

        # Pre-load character textures
        self.playerTextures = {
            "idle": loader.loadTexture(CHARACTER_IDLE_IMAGE),
            "left": loader.loadTexture(CHARACTER_LEFT_IMAGE),
            "right": loader.loadTexture(CHARACTER_RIGHT_IMAGE)
        }

        # Pre-load bonus textures
        self.bonusTextures = {
            "positive": loader.loadTexture(BONUS_POSITIVE_IMAGE),
            "negative": loader.loadTexture(BONUS_NEGATIVE_IMAGE)
        }

        # Create player sprite with idle texture
        self.player = self.createSprite(self.playerTextures["idle"],
                                         PLAYER_START_X, PLAYER_START_Y, PLAYER_SCALE)

        # Initialize camera position (Third-Person Perspective)
        self.updateCamera()
        self.originalCameraPos = self.camera.getPos() # Store original camera position

        # Create the red filter and hide it initially
        self.redFilter = self.createRedFilter()
        self.redFilter.setAlphaScale(0.0)

        # Accept keyboard events
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("enter", self.restartGame)  # Restart game when Enter is pressed
        self.accept("escape", sys.exit)

        # Game tasks
        self.taskMgr.add(self.updateTask, "updateTask")
        self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask,
                                    "autoShootTask")
        self.taskMgr.doMethodLater(ENEMY_SPAWN_INTERVAL, self.spawnEnemyTask,
                                    "spawnEnemyTask")
        self.taskMgr.doMethodLater(BONUS_SPAWN_INTERVAL, self.spawnBonusTask,
                                    "spawnBonusTask")

    def createRedFilter(self):
        """Creates the red filter overlay."""
        cm = CardMaker("red_filter")
        cm.setFrameFullscreenQuad()
        filter_node = render2d.attachNewNode(cm.generate())
        filter_node.setColor(LVecBase4f(1, 0, 0, RED_FILTER_INTENSITY))
        filter_node.setTransparency(TransparencyAttrib.MAlpha)
        return filter_node

    def startScreenShake(self):
        """Initiates the screen shake effect."""
        self.shakeStartTime = globalClock.getFrameTime()
        self.taskMgr.add(self.shakeTask, "shakeTask")

    def shakeTask(self, task):
        """Applies continuous screen shake effect."""
        currentTime = globalClock.getFrameTime()
        elapsed = currentTime - self.shakeStartTime

        if elapsed < SHAKE_DURATION:
            # Calculate decay factor (1.0 at start, 0.0 at end)
            decay = 1.0 - (elapsed / SHAKE_DURATION)
            intensity = SHAKE_INTENSITY * decay

            # Generate new random offsets with current intensity
            shake_x = random.uniform(-intensity, intensity)
            shake_y = random.uniform(-intensity, intensity)

            # Apply the shake offset to the current original camera position
            self.camera.setPos(self.originalCameraPos + Vec3(shake_x, shake_y, 0))
            return Task.cont
        else:
            # Reset camera to original position
            self.camera.setPos(self.originalCameraPos)
            return Task.done    

    def showRedFilter(self):
        """Shows the red filter."""
        self.redFilter.setAlphaScale(RED_FILTER_INTENSITY)
        self.taskMgr.doMethodLater(RED_FILTER_DURATION, self.hideRedFilter, "hideRedFilter")

    def hideRedFilter(self, task):
        """Hides the red filter."""
        self.redFilter.setAlphaScale(0.0)
        return Task.done

    def createBackground(self):
        """Creates and returns a background card using the background image."""
        bg_tex = loader.loadTexture(BACKGROUND_IMAGE)
        cm = CardMaker("background")
        # Create a unit card; we then scale it to cover the view.
        cm.setFrame(-1, 1, -1, 1)
        bg = render.attachNewNode(cm.generate())
        bg.setTexture(bg_tex)
        # Position the background using configurable parameters
        bg.setPos(BACKGROUND_POS_X, BACKGROUND_POS_Y, 0)
        bg.setScale(BACKGROUND_SCALE)
        # Set the bin so it is rendered behind game objects.
        bg.setBin("background", 0)
        bg.setDepthTest(False)
        bg.setDepthWrite(False)
        return bg

    def createSprite(self, texture, x, y, scale=1.0, transparency=1.0):
        """Creates a 2D sprite (billboarded quad) with the given texture and transparency."""
        cm = CardMaker("sprite")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        sprite = render.attachNewNode(cm.generate())
        sprite.setTexture(texture)
        # Enable transparency for PNG images
        sprite.setTransparency(TransparencyAttrib.MAlpha)
        # Set alpha for transparency
        sprite.setAlphaScale(transparency)
        sprite.setBillboardPointEye()
        sprite.setScale(scale)
        sprite.setPos(x, y, 0)
        return sprite

    def createExplosionSprite(self, x, y, enemy_scale=None, speed=EXPLOSION_SPEED):
        """
        Creates an explosion sprite with scale based on enemy size.

        Parameters:
        - x, y: Position coordinates
        - enemy_scale: Scale of the enemy that was destroyed
        - speed: Movement speed of the explosion
        """
        explosion_tex = loader.loadTexture(EXPLOSION_IMAGE)

        # Calculate explosion scale based on enemy scale
        if enemy_scale:
            # Make explosion slightly larger than the enemy for visual impact
            explosion_scale = enemy_scale * EXPLOSION_SCALE_MULTIPLIER
        else:
            # Fallback to default explosion scale
            explosion_scale = EXPLOSION_SCALE

        explosion_sprite = self.createSprite(explosion_tex, x, y, explosion_scale)
        explosion_sprite.setPythonTag("speed", speed)
        return explosion_sprite

    def createBonusSprite(self, x, y, value=BONUS_STARTING_VALUE, scale=BONUS_SCALE, speed=BONUS_SPEED):
        """
        Creates a bonus sprite with the given parameters.

        Parameters:
        - x, y: Position coordinates
        - value: Bonus value (-10 to 10)
        - scale: Sprite scale
        - speed: Movement speed
        """
        # Choose the appropriate texture based on the value
        texture = self.bonusTextures["positive"] if value > 0 else self.bonusTextures["negative"]

        # Create bonus sprite with transparency setting from configuration
        bonus_sprite = self.createSprite(texture, x, y, scale, BONUS_TRANSPARENCY)
        bonus_sprite.setPythonTag("value", value)
        bonus_sprite.setPythonTag("speed", speed)
        bonus_sprite.setPythonTag("scale", scale)

        return bonus_sprite

    def removeExplosionTask(self, explosion_sprite):
        """Task to remove the explosion sprite after a delay."""
        explosion_sprite.removeNode()
        if explosion_sprite in self.explosions:  # Remove from explosions list
            self.explosions.remove(explosion_sprite)
        return Task.done

    def setKey(self, key, value):
        """Set key state and update player texture."""
        self.keyMap[key] = value
        self.updatePlayerTexture()

    def updatePlayerTexture(self):
        """Update player texture based on key input."""
        if self.keyMap["left"]:
            self.player.setTexture(self.playerTextures["left"])
        elif self.keyMap["right"]:
            self.player.setTexture(self.playerTextures["right"])
        else:
            self.player.setTexture(self.playerTextures["idle"])

    def updateTask(self, task):
        """Main game update function."""
        if self.gameOver:
            return Task.cont

        dt = globalClock.getDt()
        self.updatePlayer(dt)
        self.updateShots(dt)
        self.updateEnemies(dt)
        self.updateExplosions(dt)
        self.updateBonuses(dt)
        self.checkCollisions()
        self.updateCamera()

        # Game Timer
        elapsed = globalClock.getRealTime() - self.gameStartTime
        self.timerText.setText(f"Time: {elapsed:.1f}")
        if elapsed >= GAME_DURATION:  # Remove check for self.enemies
            self.endGame(win=True)
        elif self.playerLife <= 0:
            self.endGame(win=False)
        return Task.cont

    def updatePlayer(self, dt):
        """Move the player left/right."""
        dx = 0
        if self.keyMap["left"]:
            dx -= PLAYER_SPEED * dt
        if self.keyMap["right"]:
            dx += PLAYER_SPEED * dt
        newX = self.player.getX() + dx
        self.player.setX(max(LEFT_BOUND, min(RIGHT_BOUND, newX)))

    def updateCamera(self):
        """Moves the camera behind and slightly above the player."""
        playerX = self.player.getX()
        self.camera.setPos(playerX, PLAYER_START_Y - CAMERA_DISTANCE,
                            CAMERA_HEIGHT)
        self.camera.lookAt(playerX, PLAYER_START_Y + CAMERA_LOOK_AT_OFFSET, 0)
        self.originalCameraPos = self.camera.getPos() # Update original position

    def updateShots(self, dt):
        """Moves shots forward and removes out-of-bounds shots."""
        for shot in self.shots[:]:
            shot.setY(shot.getY() + SHOT_SPEED * dt)
            if shot.getY() > ENEMY_SPAWN_Y + 5:
                shot.removeNode()
                self.shots.remove(shot)

    def updateEnemies(self, dt):
        """Moves enemies downward and checks for collision with the player."""
        for enemy in self.enemies[:]:
            speed = enemy.getPythonTag("speed")
            enemy.setY(enemy.getY() - speed * dt)
            # Check for collision with the player (simple horizontal distance check)
            if enemy.getY() <= PLAYER_START_Y:
                # Check collision when enemy reaches player's y coordinate
                if abs(enemy.getX() - self.player.getX()) < 1.0:
                    self.playerLife -= 1
                    self.lifeText.setText(f"Life: {self.playerLife}")
                    self.startScreenShake()
                    self.showRedFilter()
                    if self.playerLife <= 0:
                        self.endGame(win=False)
                # In either case (collision or just reaching bottom), reduce life and remove the enemy
                if enemy in self.enemies: # Check if enemy was already removed due to collision
                    self.playerLife -= 1
                    self.lifeText.setText(f"Life: {self.playerLife}")
                    self.startScreenShake()
                    self.showRedFilter()
                    enemy.removeNode()
                    self.enemies.remove(enemy)
                    if self.playerLife <= 0:
                        self.endGame(win=False)
                continue

    def updateBonuses(self, dt):
        """Moves bonuses downward and checks for collision with the player."""
        for bonus in self.bonuses[:]:
            speed = bonus.getPythonTag("speed")
            bonus.setY(bonus.getY() - speed * dt)

            # Check for collision with the player
            if bonus.getY() <= PLAYER_START_Y:
                # Check for collision at player's y position
                if abs(bonus.getX() - self.player.getX()) < 1.0:
                    self.applyBonusEffect(bonus.getPythonTag("value"))
                # Remove bonus regardless of collision
                bonus.removeNode()
                self.bonuses.remove(bonus)
                continue

            # Remove bonus if it goes out of bounds
            if bonus.getY() < PLAYER_START_Y - 10:
                bonus.removeNode()
                self.bonuses.remove(bonus)


    def applyBonusEffect(self, value):
        """Apply bonus effect to player's shot parameters based on bonus value."""
        # Calculate modifier based on bonus value (-10 = half, 0 = no change, 10 = double)
        if value == -10:  # Minimum value
            modifier = 0.5  # Halve the values
        elif value == 0:   # Neutral value
            modifier = 1.0  # No change
        elif value == 10:  # Maximum value
            modifier = 2.0  # Double the values
        else:
            # Linear interpolation for values between min and max
            # Map from -10..10 to 0.5..2.0
            modifier = 0.5 + ((value - BONUS_MIN_VALUE) / (BONUS_MAX_VALUE - BONUS_MIN_VALUE)) * 1.5

        # Apply modifiers to shot interval and scale
        self.currentShotInterval = SHOT_INTERVAL / modifier  # Lower interval = faster shots
        self.currentShotScale = SHOT_SCALE * modifier      # Higher scale = bigger shots

        # Reschedule the shot task with the new interval
        self.taskMgr.remove("autoShootTask")
        self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask, "autoShootTask")

    def updateExplosions(self, dt):
        """Moves explosions downward and removes out-of-bounds or timed-out explosions."""
        for explosion in self.explosions[:]:
            speed = explosion.getPythonTag("speed")
            explosion.setY(explosion.getY() - speed * dt)
            # Remove explosion if it goes out of bounds (similar to enemies)
            if explosion.getY() < PLAYER_START_Y - 10:
                explosion.removeNode()
                self.explosions.remove(explosion)

    def checkCollisions(self):
        """
        Checks for collisions between shots and enemies/bonuses.
        """
        for shot in self.shots[:]:
            shotPos = shot.getPos()
            shot_to_remove = False

            # Check for collision with enemies
            for enemy in self.enemies[:]:
                enemyPos = enemy.getPos()
                if (shotPos - enemyPos).length() < 0.8:  # collision threshold
                    # Reduce enemy HP by 1
                    hp = enemy.getPythonTag("hp")
                    enemy.setPythonTag("hp", hp - 1)

                    # Flag the shot for removal
                    shot_to_remove = True

                    # Check if enemy is destroyed
                    if enemy.getPythonTag("hp") <= 0:
                        # Get enemy scale for the explosion
                        enemy_scale = enemy.getScale().x  # Use x component of the scale
                        # Create explosion at enemy position with scale based on enemy size
                        explosion = self.createExplosionSprite(
                            enemy.getX(),
                            enemy.getY(),
                            enemy_scale=enemy_scale
                        )
                        self.explosions.append(explosion)
                        self.taskMgr.doMethodLater(EXPLOSION_DURATION,
                                                    self.removeExplosionTask,
                                                    "removeExplosionTask",
                                                    extraArgs=[explosion])
                        enemy.removeNode()
                        self.enemies.remove(enemy)
                        break  # Shot can only hit one enemy

            # If shot is flagged for removal, remove it and skip bonus collision check
            if shot_to_remove:
                shot.removeNode()
                self.shots.remove(shot)
                continue

            # If shot is still active, check for collision with bonuses
            for bonus in self.bonuses[:]:
                bonusPos = bonus.getPos()
                if (shotPos - bonusPos).length() < 0.8:  # collision threshold
                    # Increase bonus value by 1
                    value = bonus.getPythonTag("value")
                    new_value = min(value + 1, BONUS_MAX_VALUE)  # Cap at max value
                    bonus.setPythonTag("value", new_value)

                    # Update bonus texture based on new value
                    if value <= 0 and new_value > 0:  # Changed from negative to positive
                        bonus.setTexture(self.bonusTextures["positive"])

                    # Only remove the shot if the bonus has a negative value
                    # Positive-value bonuses allow bullets to continue
                    if new_value <= 0:
                        shot.removeNode()
                        self.shots.remove(shot)
                        break  # Shot can only hit one bonus if removed
                    # Otherwise, the shot continues and can hit more bonuses

    def autoShootTask(self, task):
        """Automatically fires a shot from the player's current position."""
        if not self.gameOver:
            shot = self.createSprite(loader.loadTexture(SHOT_IMAGE),
                                        self.player.getX(), self.player.getY(), self.currentShotScale)
            self.shots.append(shot)
        return Task.again

    def spawnEnemyTask(self, task):
        """Spawns a new enemy based on the probability distribution."""
        if self.gameOver:
            return Task.done
        etype = random.choices(list(ENEMY_TYPES.keys()), ENEMY_SPAWN_PROB)[0]
        enemyX = random.uniform(LEFT_BOUND, RIGHT_BOUND)
        enemy = self.createSprite(loader.loadTexture(ENEMY_TYPES[etype]["image"]),
                                     enemyX, ENEMY_SPAWN_Y, ENEMY_TYPES[etype]["scale"])
        enemy.setPythonTag("hp", ENEMY_TYPES[etype]["hp"])
        enemy.setPythonTag("speed", ENEMY_TYPES[etype]["speed"])
        self.enemies.append(enemy)
        return Task.again

    def spawnBonusTask(self, task):
        """Spawns a new bonus every BONUS_SPAWN_INTERVAL seconds."""
        if self.gameOver:
            return Task.done

        bonusX = random.uniform(LEFT_BOUND, RIGHT_BOUND)
        bonus = self.createBonusSprite(
            bonusX,
            ENEMY_SPAWN_Y,
            value=BONUS_STARTING_VALUE,
            scale=BONUS_SCALE,
            speed=BONUS_SPEED
        )
        self.bonuses.append(bonus)
        return Task.again

    def endGame(self, win):
        """Ends the game and displays a win/lose message."""
        self.gameOver = True
        self.lastWin = win
        if win:
            # Increase win count and stage if the player wins
            self.winCount += 1
            self.stage += 1
            self.winCountText.setText(f"Wins: {self.winCount}")
            self.statusText.setText(f"You Win! Stage {self.stage} starting soon...")
            # Automatically restart game after a short delay (3 seconds)
            self.taskMgr.doMethodLater(3.0, self.restartGameTask, "restartGameTask")
        else:
            self.statusText.setText("Game Over! Press Enter to restart.")
            # Reset stage on loss
            self.stage = 1

    def restartGameTask(self, task):
        """Task wrapper to restart the game automatically."""
        self.restartGame()
        return Task.done

    def restartGame(self):
        """Resets the game state to allow a new game to start."""
        if self.gameOver:
            # Remove remaining shots, enemies, explosions, and bonuses
            for shot in self.shots:
                shot.removeNode()
            self.shots = []

            for enemy in self.enemies:
                enemy.removeNode()
            self.enemies = []

            for explosion in self.explosions:
                explosion.removeNode()
            self.explosions = []

            for bonus in self.bonuses:
                bonus.removeNode()
            self.bonuses = []

            # Reset player position and life
            self.player.setPos(PLAYER_START_X, PLAYER_START_Y, 0)
            self.player.setTexture(self.playerTextures["idle"])
            self.playerLife = PLAYER_STARTING_LIFE
            self.lifeText.setText(f"Life: {self.playerLife}")

            # Reset shot parameters
            self.currentShotInterval = SHOT_INTERVAL
            self.currentShotScale = SHOT_SCALE

            # Reschedule the shot task with the default interval
            self.taskMgr.remove("autoShootTask")
            self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask, "autoShootTask")

            self.gameStartTime = globalClock.getRealTime()
            self.timerText.setText("Time: 0")
            self.statusText.setText("")
            self.gameOver = False

            # Remove existing enemy and bonus spawn tasks (if any)
            self.taskMgr.remove("spawnEnemyTask")
            self.taskMgr.remove("spawnBonusTask")

            # Re-schedule the game tasks with the proper intervals
            self.taskMgr.doMethodLater(ENEMY_SPAWN_INTERVAL, self.spawnEnemyTask, "spawnEnemyTask")
            self.taskMgr.doMethodLater(BONUS_SPAWN_INTERVAL, self.spawnBonusTask, "spawnBonusTask")


game = ShootingGame()
game.run()
