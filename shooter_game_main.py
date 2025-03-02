#!/usr/bin/env python3
"""
Panda3D Shooting Game with Third-Person Perspective and Background
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, Vec3, TransparencyAttrib, Point3
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

# Screen / game area bounds and positions
LEFT_BOUND = -4.0           # left-most x position for the player
RIGHT_BOUND = 4.0           # right-most x position for the player
PLAYER_START_X = 0.0          # initial player x position
PLAYER_START_Y = -10.0         # fixed player y position (bottom of play area)
ENEMY_SPAWN_Y = 26.0          # y position where enemies appear

# Camera settings (third-person view)
CAMERA_DISTANCE = 15.0         # Distance behind the player
CAMERA_HEIGHT = 10.0           # Height above the player
CAMERA_LOOK_AT_OFFSET = 5.0      # Look slightly ahead of the player

# Scales for sprites
PLAYER_SCALE = 1.0            # scale for the player sprite
SHOT_SCALE = 0.3            # scale for the shot sprite
EXPLOSION_SCALE = 0.5         # scale for the explosion sprite


# PNG filenames (ensure these files are in your assets folder)
CHARACTER_IMAGE = "assets/character.png"
SHOT_IMAGE = "assets/shot.png"
BACKGROUND_IMAGE = "assets/background.png"
EXPLOSION_IMAGE = "assets/explosion.png"  # Filename for explosion image

# Background scale constant (adjust to cover the screen)
BACKGROUND_SCALE = 100

# Enemy types: each entry contains hit points, movement speed, sprite scale, and image file
ENEMY_TYPES = {
    1: {"hp": 2,  "speed": 15.0 / 4, "scale": 0.5, "image": "assets/enemy.png"},
    2: {"hp": 4,  "speed": 12.0 / 4, "scale": 0.7, "image": "assets/enemy.png"},
    3: {"hp": 8,  "speed": 9.0 / 4,  "scale": 0.9, "image": "assets/enemy.png"},
    4: {"hp": 16, "speed": 6.0 / 3,  "scale": 1.2, "image": "assets/enemy.png"},
}

# Enemy spawn probabilities (45%, 25%, 20%, 10%)
ENEMY_SPAWN_PROB = [0.45, 0.25, 0.20, 0.10]


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
        self.keyMap = {"left": False, "right": False}

        # New feature: win and stage tracking
        self.winCount = 0      # Counts total wins (games won)
        self.stage = 1         # Current stage (starts at 1)
        self.lastWin = None    # Tracks if the last game ended in a win

        # UI elements (timer, win count and game status)
        self.timerText = OnscreenText(text="Time: 0", pos=(-1.3, 0.9),
                                         scale=0.07, mayChange=True)
        self.winCountText = OnscreenText(text="Wins: 0", pos=(1.2, 0.9),
                                            scale=0.07, mayChange=True)
        self.statusText = OnscreenText(text="", pos=(0, 0),
                                            scale=0.1, fg=(1, 0, 0, 1))

        # Create player sprite
        self.player = self.createSprite(loader.loadTexture(CHARACTER_IMAGE),
                                            PLAYER_START_X, PLAYER_START_Y, PLAYER_SCALE)

        # Initialize camera position (Third-Person Perspective)
        self.updateCamera()

        # Accept keyboard events
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("enter", self.restartGame)  # Restart game when Enter is pressed
        self.accept("escape", sys.exit)

        # Game tasks
        self.taskMgr.add(self.updateTask, "updateTask")
        self.taskMgr.doMethodLater(SHOT_INTERVAL, self.autoShootTask,
                                   "autoShootTask")
        self.taskMgr.doMethodLater(ENEMY_SPAWN_INTERVAL, self.spawnEnemyTask,
                                   "spawnEnemyTask")

    def createBackground(self):
        """Creates and returns a background card using the background image."""
        bg_tex = loader.loadTexture(BACKGROUND_IMAGE)
        cm = CardMaker("background")
        # Create a unit card; we then scale it to cover the view.
        cm.setFrame(-1, 1, -1, 1)
        bg = render.attachNewNode(cm.generate())
        bg.setTexture(bg_tex)
        # Position the background far in front of the camera’s view
        bg.setPos(0, 100, 0)
        bg.setScale(BACKGROUND_SCALE)
        # Set the bin so it is rendered behind game objects.
        bg.setBin("background", 0)
        bg.setDepthTest(False)
        bg.setDepthWrite(False)
        return bg

    def createSprite(self, texture, x, y, scale=1.0):
        """Creates a 2D sprite (billboarded quad) with the given texture."""
        cm = CardMaker("sprite")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        sprite = render.attachNewNode(cm.generate())
        sprite.setTexture(texture)
        # Enable transparency for PNG images
        sprite.setTransparency(TransparencyAttrib.MAlpha)
        sprite.setBillboardPointEye()
        sprite.setScale(scale)
        sprite.setPos(x, y, 0)
        return sprite

    def createExplosionSprite(self, x, y, scale=EXPLOSION_SCALE):
        """Creates an explosion sprite."""
        explosion_tex = loader.loadTexture(EXPLOSION_IMAGE)
        explosion_sprite = self.createSprite(explosion_tex, x, y, scale)
        return explosion_sprite

    def removeExplosionTask(self, explosion_sprite):
        """Task to remove the explosion sprite after a delay."""
        explosion_sprite.removeNode()
        return Task.done


    def setKey(self, key, value):
        self.keyMap[key] = value

    def updateTask(self, task):
        """Main game update function."""
        if self.gameOver:
            return Task.cont

        dt = globalClock.getDt()
        self.updatePlayer(dt)
        self.updateShots(dt)
        self.updateEnemies(dt)
        self.checkCollisions()
        self.updateCamera()

        # Game Timer
        elapsed = globalClock.getRealTime() - self.gameStartTime
        self.timerText.setText(f"Time: {elapsed:.1f}")
        if elapsed >= GAME_DURATION:
            self.endGame(win=True)
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
            if enemy.getY() <= PLAYER_START_Y + 0.5:
                if abs(enemy.getX() - self.player.getX()) < 1.0:
                    self.endGame(win=False)
            # Remove enemy if it goes out of bounds
            if enemy.getY() < PLAYER_START_Y - 10:
                enemy.removeNode()
                self.enemies.remove(enemy)

    def checkCollisions(self):
        """
        Checks for collisions between shots and enemies.
        A collision reduces the enemy's HP by 1.
        """
        for shot in self.shots[:]:
            shotPos = shot.getPos()
            for enemy in self.enemies[:]:
                enemyPos = enemy.getPos()
                if (shotPos - enemyPos).length() < 0.8:  # collision threshold
                    # Reduce enemy HP by 1
                    hp = enemy.getPythonTag("hp")
                    enemy.setPythonTag("hp", hp - 1)
                    shot.removeNode()
                    if shot in self.shots:
                        self.shots.remove(shot)
                    if enemy.getPythonTag("hp") <= 0:
                        # Create explosion at enemy position
                        explosion = self.createExplosionSprite(enemy.getX(), enemy.getY())
                        self.taskMgr.doMethodLater(EXPLOSION_DURATION,
                                                        self.removeExplosionTask,
                                                        "removeExplosionTask",
                                                        extraArgs=[explosion])
                        enemy.removeNode()
                        self.enemies.remove(enemy)
                    break

    def autoShootTask(self, task):
        """Automatically fires a shot from the player's current position."""
        if not self.gameOver:
            shot = self.createSprite(loader.loadTexture(SHOT_IMAGE),
                                     self.player.getX(), self.player.getY(), SHOT_SCALE)
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
            # Remove remaining shots and enemies
            for shot in self.shots:
                shot.removeNode()
            self.shots = []
            for enemy in self.enemies:
                enemy.removeNode()
            self.enemies = []
            # Reset player position and timer
            self.player.setPos(PLAYER_START_X, PLAYER_START_Y, 0)
            self.gameStartTime = globalClock.getRealTime()
            self.timerText.setText("Time: 0")
            self.statusText.setText("")
            self.gameOver = False
            # Re-schedule the enemy spawn task since it was terminated
            self.taskMgr.doMethodLater(ENEMY_SPAWN_INTERVAL, self.spawnEnemyTask,
                                       "spawnEnemyTask")


game = ShootingGame()
game.run()