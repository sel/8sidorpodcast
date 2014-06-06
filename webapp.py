#!/usr/bin/env python
# coding=utf-8

from flask import Flask, Response
import ottasidor


app = Flask(__name__)


@app.route('/')
def webroot():
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    return Response(ottasidor.genfeed(), mimetype='application/rss+xml')


#if __name__ == '__main__':
#    app.run(debug=True)
