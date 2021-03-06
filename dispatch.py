# encoding: utf-8

from flask import Flask
from flask import request
from flask import make_response
import pyes
import json
import time
from datetime import datetime
from functools import wraps
import memcache

app = Flask(__name__)
app.debug = True

es = pyes.ES('127.0.0.1:9200')
es.default_indices = ['orgdata']

mc = memcache.Client(['127.0.0.1:11211'], debug=0)


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


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def expires(f):
    """This decorator passes far future expires header"""
    timestamp = int(time.time())
    timestamp += (60 * 60 * 24 * 3)
    threedays = datetime.fromtimestamp(timestamp)
    datestring = threedays.strftime('%a, %d %m %Y %H:%M:%S GMT')
    @wraps(f)
    @add_response_headers({'Expires': datestring})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def uncached_state_facet_search():
    query = pyes.MatchAllQuery()
    query = query.search()
    query.facet.add_term_facet(field='state', name='states', size=20)
    resultset = es.search(query=query)
    return resultset.facets['states']['terms']


def uncached_search(query_term):
    if query_term == '':
        query = pyes.MatchAllQuery()
    else:
        query = pyes.WildcardQuery('name', query_term)
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


def do_search(query_term):
    key = 'openorgdata.states.numitems'
    cache = mc.get(key)
    if cache is None:
        states = uncached_state_facet_search()
        cache = {}
        for state in states:
            cache[state['term'].encode('utf-8')] = state['count']
        mc.set('openorgdata.states.numitems', cache)
    result = uncached_search(query_term)
    # merge with cache
    min_dens = 1.0
    max_dens = 0.0
    for n in range(len(result['facets']['states']['terms'])):
        name = result['facets']['states']['terms'][n]['term'].encode('utf-8')
        result['facets']['states']['terms'][n]['all'] = cache[name]
        result['facets']['states']['terms'][n]['state_id'] = state_ids[name]
        dens = (result['facets']['states']['terms'][n]['count'] /
            float(cache[name]))
        result['facets']['states']['terms'][n]['density'] = dens
        min_dens = min(min_dens, dens)
        max_dens = max(max_dens, dens)
    result['facets']['states']['density_min'] = min_dens
    result['facets']['states']['density_max'] = max_dens
    return result


@app.route('/api/')
@expires
@add_response_headers({'Content-type': 'application/json'})
def hello_world():
    q = request.args.get('q', '*')
    callback = request.args.get('callback', '')
    result = do_search(q)
    out = json.dumps(result, sort_keys=True)
    if callback != '':
        out = callback + '(' + out + ')'
    return out


if __name__ == '__main__':
    app.run()
