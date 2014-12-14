# -*- coding: utf-8 -*-

import xbmcup.app


from core.index import Index
from core.radio import Radio, RadioList


plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('radio', Radio)
plugin.route('radio-list', RadioList)

plugin.run()
