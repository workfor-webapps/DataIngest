from src.drive_functions import Create_Service, get_files#, get_temp_pdf
from src.Pdf_table_extr import extract_tables
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect
from flask.wrappers import Request
import os


app = Flask(__name__)


@app.route('/')
def index():

    return render_template('index.html')
    

@app.route('/PullTables/')
def PullTable():
    #CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
    #API_NAME = 'drive'
    #API_VERSION = 'v3'
    
    #SCOPES = ['https://www.googleapis.com/auth/drive']

    #service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    #get_files(service)
    #file1 = files[1]
    #file_id = file1["id"]
    #get_temp_pdf(service, file_id)
    #path = os.getcwd() + "/src/temp/"
    #temp_file = path + "temp.pdf"
    #table_clean = extract_tables(temp_file)
    #df = table_clean[0]
    #data = df.to_json(orient='table')

    #html_file = df.to_html()
    #text_file = open("./templates/indexT.html", "w")
    #text_file.write(html_file)
    #text_file.close()
    #return render_template('indexT.html')
    return 0#render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)