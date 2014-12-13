# -*- coding: utf-8 -*-

import xbmcup.app

class Index(xbmcup.app.Handler):
    def handle(self):
        cover = xbmcup.system.fs('home://addons/plugin.audio.lastvk/icon.png')
        self.item(u'Страна', self.link('playlists'), folder=True, cover=cover)
        self.item(u'Жанр', self.link('playlists'), folder=True, cover=cover)