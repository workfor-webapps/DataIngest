import datetime
from googleTest import google_t
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect
from flask.wrappers import Request
#import googleTest
#import Google


app = Flask(__name__)


@app.route('/')
def index():

    return render_template('index.html')
    

@app.route('/PullTables/')
def PullTable():
    html_file = google_t()
    text_file = open("./templates/indexT.html", "w")
    text_file.write(html_file)
    text_file.close()
    return render_template('indexT.html')





if __name__ == '__main__':
    app.run(debug=True)