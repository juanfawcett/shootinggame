#!/usr/bin/env python3
import sys
from panda3d.core import loadPrcFileData

from game_config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE

# Apply window configuration early
loadPrcFileData("", f"win-size {WINDOW_WIDTH} {WINDOW_HEIGHT}")
loadPrcFileData("", f"window-title {WINDOW_TITLE}")
loadPrcFileData("", "win-fixed-size 1")

from game import ShootingGame

if __name__ == "__main__":
    game = ShootingGame()
    game.run()