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
IMAGE_URL = 'https://pbs.twimg.com/profile_images/2524416759/qwmgsccjyswvznn1tfb5_400x400.jpeg'


def genfeed(max_items):
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    url = AUDIO_WEB_URL
    page = urllib2.urlopen(url).read()
    return create_feed(page, url, max_items)


def create_feed(page, url, max_items):
    soup = BeautifulSoup(page)

    feed = Feed('8 SIDOR',
                u'Lyssna på dagens lättlästa nyheter',
                url, formatdate(time.mktime(datetime.now().timetuple()), True),
                'http://pod8sidor.herokuapp.com/')

    # Set the locale to Swedish, so that textual dates can be parsed with
    # time.strptime.
    try:
        locale.setlocale(locale.LC_ALL, 'sv_SE.utf8')   # Heroku
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')  # OS X
        finally:
            pass

    # A guestimate for the item's pubDate, used in cases where the date cannot
    # be determined from either the item title or filename.  This guess is
    # updated continuously below based on the previous item's pubDate.
    item_date_guess = datetime.now()

    item_count = 0
    for a in soup.find_all('a'):
        link = a.get('href')

        if link is None or not link.endswith('.mp3'):
            continue

        filename = os.path.basename(urlparse(link).path)

        if a.string:
            title = ' '.join(a.string.splitlines()).strip()
        else:
            title = filename

        description = title

        link = urljoin(url, link)

        # Determine the item's pubDate
        try:
            # Try to convert the Swedish textual date in the title to a pubDate
            item_datetime = datetime.strptime(title, '%Aen den %d %B') \
                    .replace(year=item_date_guess.year, hour=8)
        except ValueError as e:
            # Otherwise, try to take the date from the filename instead
            try:
                item_datetime = datetime.strptime(filename, '%y%m%d.mp3')
            except:
                # Finally, fall back to our guesstimate
                item_datetime = item_date_guess

        item_pubDate = formatdate(time.mktime(item_datetime.timetuple()), True)

        feed.add_item(title, description, link, item_pubDate)

        item_count += 1
        if max_items > 0 and item_count == max_items:
            break

        item_date_guess = item_datetime - timedelta(days=1)

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

        image = ET.SubElement(self._channel, 'image')
        ET.SubElement(image, 'url').text = IMAGE_URL
        ET.SubElement(image, 'title').text = title
        ET.SubElement(image, 'link').text = link

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
