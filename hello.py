import os
import urllib2
from flask import Flask, Response
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
import xml.etree.ElementTree as ET
from email.Utils import formatdate


app = Flask(__name__)


@app.route('/')
def hello():
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    AUDIO_WEB_URL = 'http://8sidor.se/start/lyssna-pa-lattlasta-nyheter'

    root = ET.Element('rss', {
        'version': '2.0',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'})

    channel = ET.SubElement(root, 'channel')
    ET.SubElement(channel, 'title').text = "8 SIDOR"
    ET.SubElement(channel, 'description').text = "8 SIDOR"
    ET.SubElement(channel, 'link').text = AUDIO_WEB_URL
    ET.SubElement(channel, 'pubDate').text = formatdate()
    ET.SubElement(channel, 'atom:link', {
        'rel': 'self',
        'type': 'application/rss+xml',
        'href': 'http://8sidorfeed.herokuapp.com'})

    url = AUDIO_WEB_URL
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    for a in soup.find_all('a'):
        link = a.get('href')
        if link and link.endswith('.mp3'):
            if a.string:
                title = " ".join(a.string.splitlines()).encode('utf-8')
            else:
                title = os.path.basename(urlparse(link).path)

            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = title
            ET.SubElement(item, 'description').text = title
            ET.SubElement(item, 'link').text = urljoin(AUDIO_WEB_URL, link)
            ET.SubElement(item, 'guid').text = urljoin(AUDIO_WEB_URL, link)

            # TODO: Convert the Swedish textual date in the title to a pubDate
            ET.SubElement(item, 'pubDate').text = formatdate()

    return Response(ET.tostring(root), mimetype='application/rss+xml')
