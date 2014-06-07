#!/usr/bin/env python
# coding=utf-8

from flask import Flask, Response, request
import attasidor


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/')
def webroot():
    '''
    Scrape 8sidor's audio page for .mp3 links and build an RSS feed.
    '''

    try:
        max_items = int(request.args.get('max_items', '0'))
    except:
        max_items = 0

    return Response(attasidor.genfeed(max_items), mimetype='application/rss+xml')

# if __name__ == '__main__':
#    app.run(debug=True)
