#!/usr/bin/env python
# coding=utf-8

from flask import Flask, Response, request
from flask.ext.compress import Compress
import attasidor


TYPE_RSS = 'application/rss+xml'

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['COMPRESS_MIMETYPES'] = TYPE_RSS
Compress(app)


@app.route('/')
def webroot():
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    try:
        max_items = int(request.args.get('max_items', '0'))
    except:
        max_items = 0

    feed = attasidor.genfeed(max_items, request.url)

    return Response(feed, mimetype=TYPE_RSS)
