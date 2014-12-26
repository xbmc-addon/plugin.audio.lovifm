# -*- coding: utf-8 -*-

import re

import xbmcup.app
import xbmcup.db
import xbmcup.system
import xbmcup.net
import xbmcup.parser
import xbmcup.gui

import cover
from common import Render
from favorite import FavoriteAction


CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://lovifm.cache.db'))


def calc_page(page, per_page, total):
    page = page or 1
    total_pages = total/per_page
    if total_pages*per_page < total:
        total_pages += 1
    return {
        'prev': None if page == 1 else str(page - 1),
        'page': page,
        'next': None if page == total_pages else str(page + 1),
        'total': str(total_pages)
    }



class Fetch:
    def http(self, url):
        try:
            response = xbmcup.net.http.get(url)
        except xbmcup.net.http.exceptions.RequestException:
            return None
        else:
            return response.text if response.status_code == 200 else None

    def get_list(self, country, genre, page):
        if country == '0' and genre == '0':
            url = 'http://lovi.fm/stations/?sort=listens'
        elif country == '0':
            url = 'http://lovi.fm/category/' + str(genre) + '/?sort=listens'
        elif genre == '0':
            url = 'http://lovi.fm/category/' + str(country) + '/?sort=listens'
        else:
            url = 'http://lovi.fm/category/' + str(genre) + ',' + str(country) + '/?sort=listens'

        if page > 1:
            url += '&p=' + str(page) + '&scroll=1'

        html = self.http(url)
        if not html:
            return None, {'count': 0, 'data': []}
        result = {'count': 0, 'data': []}

        if page == 1:
            r = re.compile(u'Найдено станций: <b>([0-9]+)</b>', re.U|re.S).search(html)
            if not r:
                return None, result
            result['count'] = int(r.group(1))

        soup = xbmcup.parser.html(html)
        for li in soup.find_all('li', class_='station'):
            rid = li.get('data-id')
            name = li.get('data-name')
            if rid and name:
                img = li.find('img')
                result['data'].append({
                    'rid': str(rid),
                    'name': name,
                    'img': None if not img else ('http://lovi.fm' + img.get('src'))
                })

        return 2, result

    def get_radio(self, rid):
        # TODO: надо бы придумать куда выводить информацию о радио (пока эта функция используется только для resolve)
        html = self.http('http://lovi.fm/station/' + rid + '/')
        if not html:
            return ''
        soup = xbmcup.parser.html(html)
        name = soup.find('h1')
        link = soup.find(id='station' + rid)
        img = soup.find(id='js-station_logo' + rid)
        description = soup.find(class_='stationDescr')

        return {
            'rid': rid,
            'name': 'NoName' if not name else name.get_text().strip(),
            'link': None if not link else link.get('data-link'),
            'img': None if not img else ('http://lovi.fm' + img.get('src')),
            'plot': '' if not description else description.get_text().strip()
        }



class RadioList(xbmcup.app.Handler, Fetch, FavoriteAction, Render):
    def handle(self):
        self.action_favorite()
        favorite = dict.fromkeys([x['rid'] for x in self.load_favorite()], 1)

        response = CACHE(':'.join([self.argv['country'], self.argv['genre'], str(self.argv['page'])]), self.get_list, self.argv['country'], self.argv['genre'], self.argv['page'])
        count = response['count'] if self.argv['page'] == 1 else self.argv['count']
        pages = calc_page(self.argv['page'], 30, count)
        if pages['prev']:
            self.item(u'[COLOR=FF669966]' + xbmcup.app.lang[30201] + u'[/COLOR] - ' + xbmcup.app.lang[30200] + u': ' + pages['prev'] + '/' + pages['total'], self.replace('radio-list', country=self.argv['country'], genre=self.argv['genre'], page=int(pages['prev']), count=count), folder=True, cover=cover.backward)

        for radio in response['data']:
            if radio['rid'] in favorite:
                menu = [(xbmcup.app.lang[30301], self.replace('radio-list', country=self.argv['country'], genre=self.argv['genre'], page=int(pages['page']), favorite='remove', rid=radio['rid']))]
            else:
                menu = [(xbmcup.app.lang[30300], self.replace('radio-list', country=self.argv['country'], genre=self.argv['genre'], page=int(pages['page']), favorite='add', rid=radio['rid'], name=radio['name'], img=radio['img']))]
            self.item(radio['name'], self.resolve('play', rid=radio['rid']), cover=radio['img'], media='audio', info={'title': radio['name']}, menu=menu)

        if pages['next']:
            self.item(u'[COLOR=FF669966]' + xbmcup.app.lang[30202] + u'[/COLOR] - ' + xbmcup.app.lang[30200] + u': ' + pages['next'] + '/' + pages['total'], self.replace('radio-list', country=self.argv['country'], genre=self.argv['genre'], page=int(pages['next']), count=count), folder=True, cover=cover.forward)

        self.render_list()


class Radio(xbmcup.app.Handler, Fetch):
    def handle(self):
        country, genre = self.get_filter()
        self.item(country[1], self.replace('radio', mode='country'), folder=True, cover=cover.lovifm)
        self.item(genre[1], self.replace('radio', mode='genre'), folder=True, cover=cover.lovifm)
        response = CACHE(':'.join([country[0], genre[0], '1']), self.get_list, country[0], genre[0], 1)
        if response['count'] > 0:
            self.item(xbmcup.app.plural.parse(response['count'], 30000), self.link('radio-list', country=country[0], genre=genre[0], page=1), folder=True, cover=cover.lovifm)


    def get_filter(self):
        tags = self.load_tags()
        mode = self.argv.get('mode') if self.argv else None

        # country
        country = xbmcup.app.setting['country']
        if mode == 'country':
            country = self.set_setting('country', country, tags['countries'])
        country_pair = [x for x in tags['countries'] if x[0] == country]
        if not country_pair:
            country_pair = [tags['countries'][0]]

        # genre
        genre = xbmcup.app.setting['genre']
        if mode == 'genre':
            genre = self.set_setting('genre', genre, tags['genres'])
        genre_pair = [x for x in tags['genres'] if x[0] == genre]
        if not genre_pair:
            genre_pair = [tags['genres'][0]]

        return country_pair[0], genre_pair[0]


    def set_setting(self, tag, current, values):
        sel = xbmcup.gui.select(xbmcup.app.lang[30400] if tag == 'country' else xbmcup.app.lang[30401], values)
        if sel and sel != current:
            xbmcup.app.setting[tag] = sel
            current = sel
        return current


    def load_tags(self):
        result = {'countries': [], 'genres': []}
        r = xbmcup.net.http.get('http://lovi.fm/stations/')
        if r.status_code == 200:
            soup = xbmcup.parser.html(r.text)
            for a in soup.find(id='tab2').find_all('a'):
                result['countries'].append((a.get('data-id'), a.string))
            for a in soup.find(id='tab1').find_all('a'):
                result['genres'].append((a.get('data-id'), a.string))
        result['countries'] = sorted(result['countries'], key=lambda x:x[1])
        result['genres'] = sorted(result['genres'], key=lambda x:x[1])
        result['countries'].insert(0, ('0', xbmcup.app.lang[30402]))
        result['genres'].insert(0, ('0', xbmcup.app.lang[30403]))
        return result


class Play(xbmcup.app.Handler, Fetch):
    def handle(self):
        radio = self.get_radio(str(self.argv['rid']))
        return radio['link'] if radio else None
