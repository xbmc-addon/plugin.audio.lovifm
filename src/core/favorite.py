# -*- coding: utf-8 -*-

import xbmcup.db

from common import Render

DB = xbmcup.db.NoSQL(xbmcup.system.fs('sandbox://lovifm.favorite.db'))

class FavoriteAction:
    def add_favorite(self, radio):
        data = [x for x in self.load_favorite() if x['rid'] != radio['rid']]
        data.insert(0, radio)
        DB['favorite'] = data

    def remove_favorite(self, rid):
        data = [x for x in self.load_favorite() if x['rid'] != rid]
        DB['favorite'] = data

    def load_favorite(self):
        data = DB['favorite']
        return data if data else []

    def action_favorite(self):
        if self.argv and self.argv.get('favorite'):
            if self.argv['favorite'] == 'add':
                self.add_favorite({'rid': str(self.argv['rid']), 'name': self.argv['name'], 'img': self.argv['img']})
            else:
                self.remove_favorite(str(self.argv['rid']))


class Favorite(xbmcup.app.Handler, FavoriteAction, Render):
    def handle(self):
        self.action_favorite()
        for radio in self.load_favorite():
            self.item(radio['name'], self.resolve('play', rid=radio['rid']), cover=radio['img'], media='audio', info={'title': radio['name']}, menu=[(u'Удалить из закладок', self.replace('favorite', favorite='remove', rid=radio['rid']))])
        self.render_list()