# encoding: utf-8

from __future__ import with_statement

#import config
import csv
#import pyes
import hashlib
import urllib2
import simplejson as json
import sys


CSVFILE = 'orgdata_abfrage_2013-02-22.csv'
ES_HOST = '127.0.0.1:9200'
ES_INDEX = 'orgdata20130302'

LOCATION_MAPPING = {
    'Baden-Württemberg': {'id': 'bw'},
    'Bayern': {'id': 'by'},
    'Berlin': {'id': 'be'},
    'Brandenburg': {'id': 'bb'},
    'Bremen': {'id': 'hb'},
    'Hamburg': {'id': 'hh'},
    'Hessen': {'id': 'he'},
    'Mecklenburg-Vorpommern': {'id': 'mv'},
    'Niedersachsen': {'id': 'ni'},
    'Nordrhein-Westfalen': {
        'id': 'nw',
        'file': 'orgdata_locations_NRW_resolved_20130302.csv'
    },
    'Rheinland-Pfalz': {'id': 'rp'},
    'Saarland': {'id': 'sl'},
    'Sachsen': {'id': 'sn'},
    'Sachsen-Anhalt': {'id': 'st'},
    'Schleswig-Holstein': {'id': 'sh'},
    'Thüringen': {'id': 'th'}
}



def index(doc, id):
    url = 'http://' + ES_HOST + '/' + ES_INDEX + '/organisation/' + id
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=json.dumps(doc))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    try:
        url = opener.open(request)
    except urllib2.HTTPError:
        pass


def get_companies():
    with open(CSVFILE, 'rb') as csvfile:
        rowcount = 0
        reader = csv.reader(csvfile, delimiter=',', quotechar='"', doublequote=False, escapechar='\\')
        for row in reader:
            #print row
            if rowcount > 0:
                for n in range(0, len(row)):
                    row[n] = unicode(row[n].decode('utf-8'))
                yield {
                    'state': row[0],
                    'court': row[1],
                    'register_type': row[2],
                    'idnum': row[3],
                    'name': row[4],
                    'location': row[5],
                    'last_seen': row[6]
                }
            rowcount += 1


def read_csv_location_map(path):
    # use field "location" as key and "county" as value
    with open(path, 'rb') as csvfile:
        headers = []
        output = {}
        rowcount = 0
        reader = csv.reader(csvfile)
        keyfield = 0
        valuefield = 0
        for row in reader:
            if rowcount == 0:
                headers = row
                fieldcount = 0
                for field in headers:
                    if field == 'location':
                        keyfield = fieldcount
                    if field == 'county':
                        valuefield = fieldcount
                    fieldcount += 1
            else:
                output[row[keyfield]] = row[valuefield]
            rowcount += 1
        csvfile.close()
        return output


def load_location_mappings():
    for l in LOCATION_MAPPING.keys():
        if 'file' in LOCATION_MAPPING[l]:
            LOCATION_MAPPING[l]['map'] = read_csv_location_map(LOCATION_MAPPING[l]['file'])

if __name__ == '__main__':
    load_location_mappings()
    for company in get_companies():
        company['addendum'] = None
        for key in company.keys():
            if type(company[key]) == unicode:
                company[key] = company[key].encode('utf-8')
        if ' ' in company['idnum']:
            (num, addendum) = company['idnum'].split(' ', 1)
            company['idnum'] = num
            company['addendum'] = addendum
        company['idnum'] = int(company['idnum'])
        idstring = company['court'] + ' ' + company['register_type'] + ' ' + str(company['idnum'])
        if company['addendum'] is not None:
            idstring += ' ' + company['addendum']
        # string identifier
        idstring = hashlib.md5(idstring).hexdigest()
        # add county data
        if "map" in LOCATION_MAPPING[company['state']]:
            if company['location'] in LOCATION_MAPPING[company['state']]['map']:
                company['county'] = LOCATION_MAPPING[company['state']]['map'][company['location']]
                #print idstring, company['location'], company['county']
        #sys.stdout.write('.')
        index(company, idstring)
