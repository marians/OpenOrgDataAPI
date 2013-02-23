#!/var/www/openorgdata.sendung.de/venv/bin/python

# encoding: utf-8

from flup.server.fcgi import WSGIServer
from flask import Flask

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/openorgdata-fcgidsock').run(host='0.0.0.0')
    #WSGIServer(app).run()