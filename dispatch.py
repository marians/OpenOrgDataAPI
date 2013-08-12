# encoding: utf-8

from flask import Flask
from flask import request
import pyes
import json

app = Flask(__name__)
app.debug = True

es = pyes.ES('127.0.0.1:9200')


@app.route('/')
def home():
    return 'Hallo Home!'


@app.route('/api/')
def hello_world():
    q = request.args.get('q', '')
    q = pyes.TermQuery('name', q)
    results = es.search(query=q)
    return 'Hallo %s' % json.dumps(results)


if __name__ == '__main__':
    app.run()
