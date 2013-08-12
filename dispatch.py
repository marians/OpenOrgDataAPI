# encoding: utf-8

from flask import Flask

app = Flask(__name__)
app.debug = True


@app.route('/')
def home():
    return 'Hallo Home!'


@app.route('/<foo>')
def hello_world(foo):
    print "hello_world"
    return 'Hallo %s' % foo

if __name__ == '__main__':
    app.run()
