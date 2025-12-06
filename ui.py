#!/usr/bin/env python3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, LVecBase4f, TransparencyAttrib, TextNode
from game_config import BACKGROUND_IMAGE, BACKGROUND_POS_X, BACKGROUND_POS_Y, BACKGROUND_SCALE, RED_FILTER_INTENSITY

def create_background(game):
    bg_tex = loader.loadTexture(BACKGROUND_IMAGE)
    cm = CardMaker("background")
    cm.setFrame(-1, 1, -1, 1)
    bg = render.attachNewNode(cm.generate())
    bg.setTexture(bg_tex)
    bg.setPos(BACKGROUND_POS_X, BACKGROUND_POS_Y, 0)
    bg.setScale(BACKGROUND_SCALE)
    bg.setBin("background", 0)
    bg.setDepthTest(False)
    bg.setDepthWrite(False)
    return bg

def create_red_filter(game):
    cm = CardMaker("red_filter")
    cm.setFrameFullscreenQuad()
    node = render2d.attachNewNode(cm.generate())
    node.setColor(LVecBase4f(1, 0, 0, RED_FILTER_INTENSITY))
    node.setTransparency(TransparencyAttrib.MAlpha)
    return node

def create_ui_texts(game):
    timerText = OnscreenText(
        text="Time: 0",
        pos=(0.05, -0.08),
        scale=0.08,
        fg=(1, 1, 1, 1),
        align=TextNode.ALeft,
        parent=base.a2dTopLeft
    )
    winCountText = OnscreenText(
        text="Wins: 0",
        pos=(-0.05, -0.08),
        scale=0.08,
        fg=(1, 1, 1, 1),
        align=TextNode.ARight,
        parent=base.a2dTopRight
    )
    # --- NUEVO: Texto para el Top 3 ---
    highScoreText = OnscreenText(
        text="Top 3:\n--\n--\n--",
        pos=(-0.05, -0.16),      # Debajo de Wins
        scale=0.06,              # Un poco más pequeño
        fg=(1, 1, 0, 1),         # Amarillo
        align=TextNode.ARight,
        parent=base.a2dTopRight
    )
    # ----------------------------------
    lifeText = OnscreenText(
        text=f"Life: {game.playerLife}",
        pos=(0.05, -0.16),
        scale=0.08,
        fg=(1, 1, 1, 1),
        align=TextNode.ALeft,
        parent=base.a2dTopLeft
    )
    statusText = OnscreenText(
        text="",
        pos=(0, 0),
        scale=0.1,
        fg=(1, 0, 0, 1)
    )
    # Retornamos también highScoreText
    return timerText, winCountText, lifeText, statusText, highScoreText