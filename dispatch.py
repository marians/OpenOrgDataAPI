#!/var/www/openorgdata.sendung.de/venv/bin/python

# encoding: utf-8

from flup.server.fcgi import WSGIServer
from flask import Flask

app = Flask(__name__)
app.debug = True

print "default"

@app.route('/')
def home():
    print "home"
    return 'Hallo Home!'


@app.route('/<foo>')
def hello_world(foo):
    print "hello_world"
    return 'Hallo %s' % foo

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/openorgdata-fcgidsock').run()
    #WSGIServer(app).run()
