# -*- coding: utf-8 -*-

import xbmcup.app

class Render:
    def render_list(self):
        self.render(content='songs', mode=('thumb', 'list')[int(xbmcup.app.setting['render_mode'])])