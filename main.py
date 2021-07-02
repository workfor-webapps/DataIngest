import datetime
#from google.cloud import datastore
from flask import Flask, render_template, request
from flask.wrappers import Request
#import googleTest
#import Google


app = Flask(__name__)


@app.route('/')
def index():

    return render_template('index.html')
    

@app.route('/PullTables/')
    


if __name__ == '__main__':
    app.run(debug=True)