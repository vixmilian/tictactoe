[app]
title = TicTacToe
package.name = tictactoe
package.domain = org.vixmilian
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,pygame

icon.filename = %(source.dir)s/icon.png

orientation = landscape
fullscreen = 1

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
