# encoding: utf-8

from flask import Flask
from flask import request
import pyes
import json

app = Flask(__name__)
app.debug = True

es = pyes.ES('127.0.0.1:9200')
es.default_indices = ['orgdata']


@app.route('/')
def home():
    return 'Hallo Home!'


@app.route('/api/')
def hello_world():
    q = request.args.get('q', '')
    query = pyes.TermQuery('name', q)
    query = query.search()
    query.facet.add_term_facet(field='state', name='states', size=20)
    query.facet.add_term_facet(field='name', name='nameterms', size=50, order='count')
    resultset = es.search(query=query)
    return 'Hallo %s' % json.dumps(resultset.facets.nameterms.terms)


if __name__ == '__main__':
    app.run()
