#!/usr/bin/env python3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, TransparencyAttrib, TextNode

from game_config import (
    BONUS_TRANSPARENCY, BONUS_SCALE, BONUS_SPEED,
    LEFT_BOUND, RIGHT_BOUND, EXPLOSION_SCALE, EXPLOSION_SCALE_MULTIPLIER,
    BONUS_POSITIVE_IMAGE, BONUS_NEGATIVE_IMAGE, EXPLOSION_IMAGE
)

def create_sprite(game, texture, x, y, scale=1.0, transparency=1.0):
    cm = CardMaker("sprite")
    cm.setFrame(-0.5, 0.5, -0.5, 0.5)
    sprite = game.render.attachNewNode(cm.generate())
    sprite.setTexture(texture)
    sprite.setTransparency(TransparencyAttrib.MAlpha)
    sprite.setAlphaScale(transparency)
    sprite.setBillboardPointEye()
    sprite.setScale(scale)
    sprite.setPos(x, y, 0)
    return sprite

def create_explosion_sprite(game, x, y, enemy_scale=None, speed=None):
    tex = game.loader.loadTexture(EXPLOSION_IMAGE)
    if enemy_scale:
        explosion_scale = enemy_scale * EXPLOSION_SCALE_MULTIPLIER
    else:
        explosion_scale = EXPLOSION_SCALE
    explosion = create_sprite(game, tex, x, y, explosion_scale)
    explosion.setPythonTag("speed", speed if speed is not None else 0)
    return explosion

def create_bonus_sprite(game, x, y, value=0, scale=BONUS_SCALE, speed=BONUS_SPEED):
    tex_path = BONUS_POSITIVE_IMAGE if value >= 0 else BONUS_NEGATIVE_IMAGE
    tex = game.loader.loadTexture(tex_path)
    bonus = create_sprite(game, tex, x, y, scale, BONUS_TRANSPARENCY)
    bonus.setPythonTag("value", value)
    bonus.setPythonTag("speed", speed)
    bonus.setPythonTag("scale", scale)

    horiz_scale = (RIGHT_BOUND - LEFT_BOUND)
    bonus.setScale(horiz_scale, scale, scale)

    text = OnscreenText(
        text=str(value),
        scale=0.2,
        fg=(1, 1, 1, 1),
        align=TextNode.ACenter,
        mayChange=True,
        parent=bonus
    )
    text.setPos(0, -0.06)
    text.setBin('fixed', 1)
    text.setDepthTest(False)
    text.setDepthWrite(False)
    bonus.setPythonTag("text", text)
    return bonus