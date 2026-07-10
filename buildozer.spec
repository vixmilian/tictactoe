[app]
title = Tic-Tac-Toe
package.name = game
package.domain = com.tictactoe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = all
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
