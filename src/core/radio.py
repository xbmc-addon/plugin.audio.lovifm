# -*- coding: utf-8 -*-

import re

import xbmcup.app
import xbmcup.system
import xbmcup.net
import xbmcup.parser
import xbmcup.gui

import cover


class Fetch:
    def fetch(self, country, genre, page):
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

        response = xbmcup.net.http.get(url)
        if response.status_code != 200:
            return {'count': 0, 'data': []}
        result = {'count': 0, 'data': []}

        if page == 1:
            r = re.compile(u'Найдено станций: <b>([0-9]+)</b>', re.U|re.S).search(response.text)
            if not r:
                return result
            result['count'] = int(r.group(1))

        soup = xbmcup.parser.html(response.text)
        for li in soup.find_all('li'):
            link = li.get('data-link')
            name = li.get('data-name')
            if link and name:
                img = li.find('img')
                if img:
                    img = 'http://lovi.fm' + img.get('src')
                result['data'].append({
                    'link': link,
                    'name': name,
                    'img': img
                })

        return result


class RadioList(xbmcup.app.Handler, Fetch):
    def handle(self):
        response = self.fetch(self.argv['country'], self.argv['genre'], self.argv['page'])
        for item in response['data']:
            self.item(item['name'], self.play(item['link']), cover=item['img'])
        self.render()


class Radio(xbmcup.app.Handler, Fetch):
    def handle(self):
        country, genre = self.get_filter()
        self.item(country[1], self.replace('radio', mode='country'), folder=True, cover=cover.lovifm)
        self.item(genre[1], self.replace('radio', mode='genre'), folder=True, cover=cover.lovifm)
        response = self.fetch(country[0], genre[0], 1)
        if response['count'] > 0:
            self.item(xbmcup.app.plural.parse(response['count'], 30001), self.link('radio-list', country=country[0], genre=genre[0], page=1), folder=True, cover=cover.lovifm)


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
        sel = xbmcup.gui.select(u'Выберите страну' if tag == 'country' else u'Выберите жанр', values)
        if sel and sel != current:
            xbmcup.app.setting[tag] = sel
            current = sel
        return current


    def load_tags(self):
        result = {'countries': [('0', u'Все страны')], 'genres': [('0', u'Все жанры')]}
        r = xbmcup.net.http.get('http://lovi.fm/stations/')
        if r.status_code == 200:
            soup = xbmcup.parser.html(r.text)
            for a in soup.find(id='tab2').find_all('a'):
                result['countries'].append((a.get('data-id'), a.string))
            for a in soup.find(id='tab1').find_all('a'):
                result['genres'].append((a.get('data-id'), a.string))
        return {
            'countries': sorted(result['countries'], key=lambda x:x[1]),
            'genres': sorted(result['genres'], key=lambda x:x[1])
        }
