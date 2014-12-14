# -*- coding: utf-8 -*-

import xbmcup.app

import cover

class Index(xbmcup.app.Handler):
    def handle(self):
        self.item(u'Радиостанции', self.link('radio'), folder=True, cover=cover.lovifm)
        self.item(u'Закладки', self.link('favorite'), folder=True, cover=cover.favorite)
