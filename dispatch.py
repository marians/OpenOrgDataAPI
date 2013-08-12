# encoding: utf-8

from flask import Flask
from flask import request
import pyes
import json

app = Flask(__name__)
app.debug = True

esconn = pyes.ES('127.0.0.1:9200')


@app.route('/')
def home():
    return 'Hallo Home!'


@app.route('/api/')
def hello_world():
    print "hello_world"
    q = request.args.get('q', '')
    return 'Hallo %s' % q


if __name__ == '__main__':
    app.run()
