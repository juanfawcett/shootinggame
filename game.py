#!/usr/bin/env python3
import random
import sys
import json  # <--- Necesario
import os    # <--- Necesario
import copy
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, LVecBase4f, TransparencyAttrib, Vec3

from game_config import (
    GAME_DURATION, SHOT_INTERVAL, ENEMY_SPAWN_INTERVAL,
    PLAYER_SPEED, SHOT_SPEED, EXPLOSION_DURATION,
    EXPLOSION_SPEED, BONUS_SPAWN_INTERVAL,
    SHAKE_INTENSITY, SHAKE_DURATION,
    RED_FILTER_INTENSITY, RED_FILTER_DURATION,
    LEFT_BOUND, RIGHT_BOUND, PLAYER_START_X,
    PLAYER_START_Y, ENEMY_SPAWN_Y, BONUS_SPAWN_POSITIONS,
    CAMERA_DISTANCE, CAMERA_HEIGHT, CAMERA_LOOK_AT_OFFSET,
    PLAYER_SCALE, SHOT_SCALE, EXPLOSION_SCALE, EXPLOSION_SCALE_MULTIPLIER, BONUS_SCALE,
    BONUS_STARTING_VALUE, BONUS_MAX_VALUE, BONUS_MIN_VALUE, BONUS_SPEED, BONUS_TRANSPARENCY,
    CHARACTER_IDLE_IMAGE, CHARACTER_LEFT_IMAGE, CHARACTER_RIGHT_IMAGE,
    SHOT_IMAGE, EXPLOSION_IMAGE, BONUS_POSITIVE_IMAGE, BONUS_NEGATIVE_IMAGE,
    BACKGROUND_IMAGE, BACKGROUND_POS_X, BACKGROUND_POS_Y, BACKGROUND_SCALE,
    ENEMY_TYPES, ENEMY_SPAWN_PROB, PLAYER_STARTING_LIFE,
    DIFFICULTY_PRESETS, DEFAULT_DIFFICULTY
)

from sprites import create_sprite, create_explosion_sprite, create_bonus_sprite
from ui import create_background, create_red_filter, create_ui_texts

class ShootingGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # State
        self.gameOver = False
        self.menuActive = True
        self.difficultyName = DEFAULT_DIFFICULTY
        self.difficultyPreset = DIFFICULTY_PRESETS[self.difficultyName]
        self.basePlayerLife = PLAYER_STARTING_LIFE

        self.gameStartTime = globalClock.getRealTime()
        self.shots = []
        self.enemies = []
        self.explosions = []
        self.bonuses = []
        self.keyMap = {"left": False, "right": False}
        self.playerLife = 0  # se setea cuando se selecciona dificultad

        self.currentShotInterval = SHOT_INTERVAL
        self.currentShotScale = SHOT_SCALE

        self.winCount = 0
        self.stage = 1
        self.lastWin = None

        # --- Score Acumulativo ---
        self.accumulatedTime = 0.0

        # Background & UI (use helpers)
        self.background = create_background(self)
        # Desempaquetamos la nueva variable highScoreText
        self.timerText, self.winCountText, self.lifeText, self.statusText, self.highScoreText,self.difficultText = create_ui_texts(self)

        # Actualizar texto de Top 3 al inicio
        self.update_high_score_text()

        # Textures
        self.playerTextures = {
            "idle": loader.loadTexture(CHARACTER_IDLE_IMAGE),
            "left": loader.loadTexture(CHARACTER_LEFT_IMAGE),
            "right": loader.loadTexture(CHARACTER_RIGHT_IMAGE)
        }
        self.bonusTextures = {
            "positive": loader.loadTexture(BONUS_POSITIVE_IMAGE),
            "negative": loader.loadTexture(BONUS_NEGATIVE_IMAGE)
        }

        # Player
        self.player = create_sprite(self, self.playerTextures["idle"], PLAYER_START_X, PLAYER_START_Y, PLAYER_SCALE)

        # Camera
        self.updateCamera()
        self.originalCameraPos = self.camera.getPos()

        # Red filter
        self.redFilter = create_red_filter(self)
        self.redFilter.setAlphaScale(0.0)

        # Input
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        # enter: si el menú está activo, inicia con la dificultad por defecto; si el juego terminó, reinicia.
        self.accept("enter", self.handleEnter)
        self.accept("escape", sys.exit)
        # teclas para seleccionar dificultad desde el menú
        self.accept("1", self.onDifficultyKey, ["Easy"])
        self.accept("2", self.onDifficultyKey, ["Medium"])
        self.accept("3", self.onDifficultyKey, ["Hard"])

        # Tasks
        self.taskMgr.add(self.updateTask, "updateTask")
        # Las tareas de autoShoot y spawn se iniciarán después de seleccionar dificultad

        # Menu UI (antes de empezar el juego)
        self.createDifficultyMenu()

    # --- Persistencia de Datos (JSON) ---
    def load_scores(self):
        if os.path.exists("highscores.json"):
            try:
                with open("highscores.json", "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_score(self, score):
        scores = self.load_scores()
        scores.append(score)
        scores.sort(reverse=True)
        scores = scores[:3]  # Guardar solo Top 3
        with open("highscores.json", "w") as f:
            json.dump(scores, f)
        self.update_high_score_text()

    def update_high_score_text(self):
        scores = self.load_scores()
        # Formatear texto para mostrar los 3 mejores
        text_content = "Top 3:\n"
        for i in range(3):
            if i < len(scores):
                text_content += f"{i+1}. {scores[i]}s\n"
            else:
                text_content += f"{i+1}. --\n"
        self.highScoreText.setText(text_content)

    # --- UI / camera / input helpers ---
    def setKey(self, key, value):
        self.keyMap[key] = value
        self.updatePlayerTexture()

    def updatePlayerTexture(self):
        if self.keyMap["left"]:
            self.player.setTexture(self.playerTextures["left"])
        elif self.keyMap["right"]:
            self.player.setTexture(self.playerTextures["right"])
        else:
            self.player.setTexture(self.playerTextures["idle"])

    def updateCamera(self):
        playerX = self.player.getX()
        self.camera.setPos(playerX, PLAYER_START_Y - CAMERA_DISTANCE, CAMERA_HEIGHT)
        self.camera.lookAt(playerX, PLAYER_START_Y + CAMERA_LOOK_AT_OFFSET, 0)
        self.originalCameraPos = self.camera.getPos()

    # --- Effects ---
    def startScreenShake(self):
        self.shakeStartTime = globalClock.getFrameTime()
        self.taskMgr.add(self.shakeTask, "shakeTask")

    def shakeTask(self, task):
        currentTime = globalClock.getFrameTime()
        elapsed = currentTime - self.shakeStartTime
        if elapsed < SHAKE_DURATION:
            decay = 1.0 - (elapsed / SHAKE_DURATION)
            intensity = SHAKE_INTENSITY * decay
            shake_x = random.uniform(-intensity, intensity)
            shake_y = random.uniform(-intensity, intensity)
            self.camera.setPos(self.originalCameraPos + Vec3(shake_x, shake_y, 0))
            return Task.cont
        else:
            self.camera.setPos(self.originalCameraPos)
            return Task.done

    def showRedFilter(self):
        self.redFilter.setAlphaScale(RED_FILTER_INTENSITY)
        self.taskMgr.doMethodLater(RED_FILTER_DURATION, self.hideRedFilter, "hideRedFilter")

    def hideRedFilter(self, task):
        self.redFilter.setAlphaScale(0.0)
        return Task.done

    # --- Main update loop ---
    def updateTask(self, task):
        if self.menuActive:
            return Task.cont
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

        elapsed = globalClock.getRealTime() - self.gameStartTime
        self.timerText.setText(f"Time: {elapsed:.1f}")
        if elapsed >= GAME_DURATION:
            self.endGame(win=True)
        elif self.playerLife <= 0:
            self.endGame(win=False)
        return Task.cont

    # --- Movement updates ---
    def updatePlayer(self, dt):
        dx = 0
        if self.keyMap["left"]:
            dx -= PLAYER_SPEED * dt
        if self.keyMap["right"]:
            dx += PLAYER_SPEED * dt
        newX = self.player.getX() + dx
        self.player.setX(max(LEFT_BOUND, min(RIGHT_BOUND, newX)))

    def updateShots(self, dt):
        for shot in self.shots[:]:
            shot.setY(shot.getY() + SHOT_SPEED * dt)
            if shot.getY() > ENEMY_SPAWN_Y + 5:
                shot.removeNode()
                self.shots.remove(shot)

    def updateEnemies(self, dt):
        for enemy in self.enemies[:]:
            speed = enemy.getPythonTag("speed")
            enemy.setY(enemy.getY() - speed * dt)
            if enemy.getY() <= PLAYER_START_Y:
                if abs(enemy.getX() - self.player.getX()) < 1.0:
                    self.playerLife -= 1
                    self.lifeText.setText(f"Life: {self.playerLife}")
                    self.startScreenShake()
                    self.showRedFilter()
                    enemy.removeNode()
                    self.enemies.remove(enemy)
                    if self.playerLife <= 0:
                        self.endGame(win=False)
                    continue
                if enemy in self.enemies:
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
        for bonus in self.bonuses[:]:
            speed = bonus.getPythonTag("speed")
            bonus.setY(bonus.getY() - speed * dt)
            if bonus.getY() <= PLAYER_START_Y:
                if abs(bonus.getX() - self.player.getX()) < 1.0:
                    self.applyBonusEffect(bonus.getPythonTag("value"))
                text = bonus.getPythonTag("text")
                if text:
                    text.destroy()
                bonus.removeNode()
                self.bonuses.remove(bonus)
                continue
            if bonus.getY() < PLAYER_START_Y - 10:
                text = bonus.getPythonTag("text")
                if text:
                    text.destroy()
                bonus.removeNode()
                self.bonuses.remove(bonus)

    def updateExplosions(self, dt):
        for explosion in self.explosions[:]:
            speed = explosion.getPythonTag("speed")
            explosion.setY(explosion.getY() - speed * dt)
            if explosion.getY() < PLAYER_START_Y - 10:
                explosion.removeNode()
                self.explosions.remove(explosion)

    # --- Collisions ---
    def checkCollisions(self):
        for shot in self.shots[:]:
            shotPos = shot.getPos()
            shot_to_remove = False
            for enemy in self.enemies[:]:
                enemyPos = enemy.getPos()
                if (shotPos - enemyPos).length() < 0.55:
                    hp = enemy.getPythonTag("hp")
                    enemy.setPythonTag("hp", hp - 1)
                    shot_to_remove = True
                    if enemy.getPythonTag("hp") <= 0:
                        enemy_scale = enemy.getScale().x
                        explosion = create_explosion_sprite(self, enemy.getX(), enemy.getY(), enemy_scale)
                        self.explosions.append(explosion)
                        self.taskMgr.doMethodLater(EXPLOSION_DURATION, lambda t, e=explosion: (e.removeNode(), self.explosions.remove(e), Task.done)[2], "removeExplosionTask")
                        enemy.removeNode()
                        self.enemies.remove(enemy)
                        break
            if shot_to_remove:
                shot.removeNode()
                self.shots.remove(shot)
                continue
            for bonus in self.bonuses[:]:
                bonusPos = bonus.getPos()
                if (shotPos - bonusPos).length() < 2:
                    value = bonus.getPythonTag("value")
                    new_value = min(value + 1, BONUS_MAX_VALUE)
                    bonus.setPythonTag("value", new_value)
                    if new_value > 0:
                        bonus.setTexture(self.bonusTextures["positive"])
                    else:
                        bonus.setTexture(self.bonusTextures["negative"])
                    text = bonus.getPythonTag("text")
                    if text:
                        text.setText(str(new_value))
                    shot.removeNode()
                    self.shots.remove(shot)
                    break

    # --- Tasks that spawn / shoot ---
    def autoShootTask(self, task):
        if not self.gameOver and not self.menuActive:
            shot = create_sprite(self, loader.loadTexture(SHOT_IMAGE), self.player.getX(), self.player.getY(), self.currentShotScale)
            self.shots.append(shot)
        return Task.again

    def spawnEnemyTask(self, task):
        if self.gameOver or self.menuActive:
            return Task.done
        etype = random.choices(list(self.enemy_types.keys()), ENEMY_SPAWN_PROB)[0]
        enemyX = random.uniform(LEFT_BOUND, RIGHT_BOUND)
        cfg = self.enemy_types[etype]
        enemy = create_sprite(self, loader.loadTexture(cfg["image"]), enemyX, ENEMY_SPAWN_Y, cfg["scale"])
        enemy.setPythonTag("hp", cfg["hp"])
        enemy.setPythonTag("speed", cfg["speed"])
        self.enemies.append(enemy)
        return Task.again

    def spawnBonusTask(self, task):
        if self.gameOver:
            return Task.done
        bonusX = random.choice(BONUS_SPAWN_POSITIONS)
        bonus = create_bonus_sprite(self, bonusX, ENEMY_SPAWN_Y, value=BONUS_STARTING_VALUE)
        self.bonuses.append(bonus)
        return Task.again

    # --- Bonuses / end / restart ---
    def applyBonusEffect(self, value):
        if value == BONUS_MIN_VALUE:
            modifier = 0.5
        elif value == 0:
            modifier = 1.0
        elif value == BONUS_MAX_VALUE:
            modifier = 2.0
        else:
            modifier = 0.5 + ((value - BONUS_MIN_VALUE) / (BONUS_MAX_VALUE - BONUS_MIN_VALUE)) * 1.5
        self.currentShotInterval = SHOT_INTERVAL / modifier
        self.currentShotScale = SHOT_SCALE * modifier
        self.taskMgr.remove("autoShootTask")
        self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask, "autoShootTask")

    def endGame(self, win):
        self.gameOver = True
        self.lastWin = win

        # 1. Calcular el tiempo total real (Acumulado + Actual)
        current_stage_time = globalClock.getRealTime() - self.gameStartTime
        total_score_real = self.accumulatedTime + current_stage_time
        final_score_display = round(total_score_real, 2)

        # 2. Guardar el puntaje (siempre guardamos el total logrado)
        self.save_score(final_score_display)

        if win:
            # Si gana, acumulamos el tiempo para la siguiente ronda
            self.accumulatedTime += current_stage_time

            self.winCount += 1
            self.stage += 1
            self.winCountText.setText(f"Wins: {self.winCount}")
            self.statusText.setText(f"You Win! Total: {final_score_display}s. Next stage...")
            self.taskMgr.doMethodLater(3.0, self.restartGameTask, "restartGameTask")
        else:
            self.statusText.setText(f"Game Over! Final: {final_score_display}s. Press Enter.")
            # Si pierde, marcamos stage 1 para borrar el acumulado al reiniciar
            self.stage = 1

    def restartGameTask(self, task):
        self.restartGame()
        return Task.done

    def restartGame(self):
        if self.gameOver:
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
                text = bonus.getPythonTag("text")
                if text:
                    text.destroy()
                bonus.removeNode()
            self.bonuses = []
            self.player.setPos(PLAYER_START_X, PLAYER_START_Y, 0)
            self.player.setTexture(self.playerTextures["idle"])
            self.playerLife = PLAYER_STARTING_LIFE
            self.lifeText.setText(f"Life: {self.playerLife}")
            self.currentShotInterval = SHOT_INTERVAL
            self.currentShotScale = SHOT_SCALE
            self.taskMgr.remove("autoShootTask")
            self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask, "autoShootTask")
            self.gameStartTime = globalClock.getRealTime()
            self.timerText.setText("Time: 0")
            self.statusText.setText("")
            self.gameOver = False

            # --- Lógica de Reinicio de Acumulado ---
            if self.stage == 1:
                self.accumulatedTime = 0.0
                self.winCount = 0
                self.winCountText.setText("Wins: 0")
            # ---------------------------------------

            self.taskMgr.remove("spawnEnemyTask")
            self.taskMgr.remove("spawnBonusTask")
            self.taskMgr.doMethodLater(ENEMY_SPAWN_INTERVAL, self.spawnEnemyTask, "spawnEnemyTask")
            self.taskMgr.doMethodLater(BONUS_SPAWN_INTERVAL, self.spawnBonusTask, "spawnBonusTask")

    # --- Nuevo: menú / dificultad ---
    def createDifficultyMenu(self):
        # Textos del menú
        self.menuTitle = OnscreenText(text="Select Difficulty", scale=0.12, pos=(0, 0.6), fg=(1,1,0,1), mayChange=False)
        self.menuOption1 = OnscreenText(text="1 - Easy", scale=0.08, pos=(0, 0.2), fg=(0.6,1,0.6,1), mayChange=False)
        self.menuOption2 = OnscreenText(text="2 - Medium (default)", scale=0.08, pos=(0, 0.0), fg=(1,1,1,1), mayChange=False)
        self.menuOption3 = OnscreenText(text="3 - Hard", scale=0.08, pos=(0, -0.2), fg=(1,0.6,0.6,1), mayChange=False)
        self.menuHint = OnscreenText(text="Press 1/2/3 or Enter to start", scale=0.06, pos=(0, -0.45), fg=(1,1,1,1), mayChange=False)

    def destroyDifficultyMenu(self):
        for node in [getattr(self, n) for n in ("menuTitle","menuOption1","menuOption2","menuOption3","menuHint") if hasattr(self,n)]:
            try:
                node.destroy()
            except Exception:
                pass

    def onDifficultyKey(self, name):
        if not self.menuActive:
            return
        self.applyDifficulty(name)
        self.startGame()

    def handleEnter(self):
        if self.menuActive:
            # iniciar con la dificultad por defecto
            self.applyDifficulty(DEFAULT_DIFFICULTY)
            self.startGame()
            return
        if self.gameOver:
            self.restartGame()

    def applyDifficulty(self, name):
        preset = DIFFICULTY_PRESETS.get(name, DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])
        self.difficultyName = name
        self.difficultyPreset = preset
        # copiar y escalar enemy types (no tocamos config original)
        self.enemy_types = copy.deepcopy(ENEMY_TYPES)
        for k, v in self.enemy_types.items():
            v["speed"] = v["speed"] * preset["enemy_speed_mul"]
        # ajustar intervalos y disparo
        self.currentEnemySpawnInterval = ENEMY_SPAWN_INTERVAL * preset["enemy_spawn_interval_mul"]
        self.currentShotInterval = SHOT_INTERVAL * preset["shot_interval_mul"]
        self.basePlayerLife = preset["player_life"]
        self.playerLife = self.basePlayerLife
        self.lifeText.setText(f"Life: {self.playerLife}")
        # actualizar texto de estado
        self.difficultText.setText(f"Difficulty: {name}")

    def startGame(self):
        # ocultar menú y arrancar tareas principales
        self.destroyDifficultyMenu()
        self.menuActive = False
        self.gameStartTime = globalClock.getRealTime()
        # arrancar tareas con los intervalos adaptados
        self.taskMgr.remove("autoShootTask")
        self.taskMgr.doMethodLater(self.currentShotInterval, self.autoShootTask, "autoShootTask")
        self.taskMgr.remove("spawnEnemyTask")
        self.taskMgr.doMethodLater(self.currentEnemySpawnInterval, self.spawnEnemyTask, "spawnEnemyTask")
        self.taskMgr.remove("spawnBonusTask")
        self.taskMgr.doMethodLater(BONUS_SPAWN_INTERVAL, self.spawnBonusTask, "spawnBonusTask")
