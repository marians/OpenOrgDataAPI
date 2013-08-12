# encoding: utf-8

from flask import Flask
from flask import request
import pyes
import json

app = Flask(__name__)
app.debug = True

es = pyes.ES('127.0.0.1:9200')
es.default_indices = ['orgdata']


state_ids = {
    'Baden-Württemberg': 'bw',
    'Bayern': 'by',
    'Berlin': 'be',
    'Brandenburg': 'bb',
    'Bremen': 'hb',
    'Hamburg': 'hh',
    'Hessen': 'he',
    'Mecklenburg-Vorpommern': 'mv',
    'Niedersachsen': 'ni',
    'Nordrhein-Westfalen': 'nw',
    'Rheinland-Pfalz': 'rp',
    'Saarland': 'sl',
    'Sachsen': 'sn',
    'Sachsen-Anhalt': 'st',
    'Schleswig-Holstein': 'sh',
    'Thüringen': 'th'
}


def do_search(query_term):
    query = pyes.TermQuery('name', query_term)
    query = query.search()
    query.facet.add_term_facet(field='state', name='states', size=20)
    query.facet.add_term_facet(field='name', name='nameterms', size=50, order='count')
    resultset = es.search(query=query)
    result = {
        'took': resultset.took,
        'timed_out': resultset.timed_out,
        'hits': resultset.total,
        'facets': resultset.facets
    }
    return result


@app.route('/')
def home():
    return 'Hallo Home!'


@app.route('/api/')
def hello_world():
    q = request.args.get('q', '*')
    result = do_search(q)

    # TODO: mime type
    # TODO: expires header
    return 'Hallo <br> <code>%s</code> <br> <code>%s</code>' % (
        json.dumps(resultset.facets.nameterms),
        json.dumps(resultset.facets.states)
    )


if __name__ == '__main__':
    app.run()
