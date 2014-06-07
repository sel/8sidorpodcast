#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
import xml.etree.ElementTree as ET
from email.Utils import formatdate
from datetime import datetime, timedelta
import time
import locale


AUDIO_WEB_URL = 'http://8sidor.se/start/lyssna-pa-lattlasta-nyheter'


def genfeed():
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    url = AUDIO_WEB_URL
    page = urllib2.urlopen(url).read()
    return create_feed(page, url)


def create_feed(page, url):
    soup = BeautifulSoup(page)
    pubDate = datetime.now()

    feed = Feed('8 SIDOR',
                u'Lyssna på dagens lättlästa nyheter',
                url, formatdate(time.mktime(pubDate.timetuple()), True),
                'http://pod8sidor.herokuapp.com/')

    locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')

    for a in soup.find_all('a'):
        link = a.get('href')

        if link is None or not link.endswith('.mp3'):
            continue

        if a.string:
            title = ' '.join(a.string.splitlines()).strip()
        else:
            title = os.path.basename(urlparse(link).path)

        description = title

        link = urljoin(url, link)

        # Try to convert the Swedish textual date in the title to a pubDate
        try:
            dt = datetime.strptime(title, '%Aen den %d %B')
            dt = dt.replace(year=pubDate.year, hour=8)
            item_pubdate = formatdate(time.mktime(dt.timetuple()), True)
        except ValueError as e:
            print e
            item_pubdate = formatdate(time.mktime(pubDate.timetuple()), True)

        feed.add_item(title, description, link, item_pubdate)

        pubDate = pubDate - timedelta(days=1)

    return feed.to_string()


class Feed():

    def __init__(self, title, description, link, pubdate, self_link):
        self._root = ET.Element('rss', {
            'version': '2.0',
            'xmlns:atom': 'http://www.w3.org/2005/Atom'})

        self._channel = ET.SubElement(self._root, 'channel')
        ET.SubElement(self._channel, 'title').text = title
        ET.SubElement(self._channel, 'description').text = description
        ET.SubElement(self._channel, 'link').text = link
        ET.SubElement(self._channel, 'pubDate').text = pubdate
        ET.SubElement(self._channel, 'atom:link', {
            'rel': 'self',
            'type': 'application/rss+xml',
            'href': self_link})

    def add_item(self, title, description, link, pubdate):
        item = ET.SubElement(self._channel, 'item')
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'description').text = description
        ET.SubElement(item, 'link').text = link
        ET.SubElement(item, 'pubDate').text = pubdate
        ET.SubElement(item, 'guid', {'isPermalink': 'false'}).text = link
        ET.SubElement(item, 'enclosure', {
            'url': link, 'type': 'audio/mpeg',
            'length': '100000'})

    def to_string(self):
        return '<?xml version="1.0" encoding="UTF-8"?>' + \
            ET.tostring(self._root, 'utf-8')
