# -*- coding: utf-8 -*-

import xbmcup.app


from core.index import Index
from core.radio import Radio, RadioList, Play
from core.favorite import Favorite


plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('radio', Radio)
plugin.route('radio-list', RadioList)
plugin.route('play', Play)
plugin.route('favorite', Favorite)

plugin.run()

"""
TODO

1. Профайлы радиостанций
2. Вид вывода в настройках
3. Добавление в фавориты
4. Вывод фаворитов
5. Сделать нормальную локализацию

"""