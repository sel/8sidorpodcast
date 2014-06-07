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


# URL of the page containing the daily audio news
AUDIO_PAGE_URL = 'http://8sidor.se/start/lyssna-pa-lattlasta-nyheter'

# 8sidor logo
IMAGE_URL = 'https://pbs.twimg.com/profile_images/2524416759/' + \
    'qwmgsccjyswvznn1tfb5_400x400.jpeg'

# Default title and description used in the case that they cannot be determined
# from the HTML page.
DEFAULT_TITLE = u'8 SIDOR'
DEFAULT_DESCR = u'Lyssna på dagens lättlästa nyheter'

# Set an average file size for the enclosure length used in the feed, since the
# file length is not available in the HTML page and it would take too long to
# work out the correct size of all linked media files.
DEFAULT_AUDIO_SIZE = '2621440'  # 2.5MB


def genfeed(max_items, self_url):
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    url = AUDIO_PAGE_URL
    resp = urllib2.urlopen(url)
    page_date = resp.info().getheader('Date')
    return create_feed(resp.read(), page_date, url, max_items, self_url)


def create_feed(page, page_date, url, max_items, self_url):
    # Set the locale to Swedish, so that textual dates can be parsed with
    # datetime.strptime.  For some reason the locale names are different in
    # Heroku and OS X.
    try:
        locale.setlocale(locale.LC_ALL, 'sv_SE.utf8')   # Heroku
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')  # OS X
        finally:
            pass

    soup = BeautifulSoup(page)

    try:
        title = soup.title.string.strip()
    except:
        title = DEFAULT_TITLE

    try:
        description = soup.head.meta.find(attrs={"name": "description"}) \
            .get('content')
    except:
        description = DEFAULT_DESCR

    last_build_date = formatdate(time.mktime(datetime.now().timetuple()), True)
    pub_date = page_date or last_build_date

    feed = Feed(title, description, url, pub_date, last_build_date, self_url)

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

    def __init__(self, title, description, link, pub_date, last_build_date,
                 self_link):

        self._root = ET.Element('rss', {
            'version': '2.0',
            'xmlns:atom': 'http://www.w3.org/2005/Atom'})

        self._channel = ET.SubElement(self._root, 'channel')
        ET.SubElement(self._channel, 'title').text = title
        ET.SubElement(self._channel, 'description').text = description
        ET.SubElement(self._channel, 'link').text = link
        ET.SubElement(self._channel, 'pubDate').text = pub_date
        ET.SubElement(self._channel, 'lastBuildDate').text = last_build_date
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
            'length': DEFAULT_AUDIO_SIZE})

    def to_string(self):
        return '<?xml version="1.0" encoding="UTF-8"?>' + \
            ET.tostring(self._root, 'utf-8')
