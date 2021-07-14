from src.drive_functions import Create_Service, get_files, get_temp_pdf
from src.Pdf_table_extr import extract_tables, get_title
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect
from flask.wrappers import Request
import os


app = Flask(__name__)


@app.route('/')
def index():

    return render_template('index.html',pdf_list=[])
    

@app.route('/PullTables')  #  https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
def PullTable():
    #CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
    #API_NAME = 'drive'
    #API_VERSION = 'v3'
    
    #SCOPES = ['https://www.googleapis.com/auth/drive']

    #service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    #files = get_files(service)
    #file1 = files[0]
    #file_id = file1["id"]
    #get_temp_pdf(service, file_id)
     #path = os.getcwd() + "/temp/"
    #temp_file = "/tmp/temp.pdf"
    #paper_title = get_title(temp_file)
    #table_clean = extract_tables(temp_file)
    #df = table_clean[0]
#
#     #-----------------Get json for table-------------
    #data = df.to_json(orient='table')
#     #------------------------------------------------
#
    #html_file = df.to_html(index=False, justify="left", na_rep="", classes="table table-light table-striped table-hover table-bordered table-responsive-lg", table_id="pdf")
    #text_file = open("./templates/table_temp.html", "w")
    #header = '<!DOCTYPE html>\n<html lang="en">\n'
    #text_file.write(header)
    #text_file.write(html_file)
    #text_file.close()'''
    #paths = os.getcwd() + "/src/temp/Capture.PNG"
    return render_template('indexT.html', title="paper_title")

@app.route('/list_pdfs')
def list():
    """CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    files = get_files(service)
    #pdfs = [name for name in files["name"]] """
    files = ["A.pdf", "B.pdf"]
    return render_template('index.html', pdf_list= files) 



@app.route('/post_json', methods = ['POST'])
def post_json():
    if request.method == 'POST':
        table = request.get_json()
        print(type(table))
        
        import pandas as pd
        df = pd.DataFrame(table)
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
        #import csv
        df.to_excel("table.xlsx" , index=False)
        #with open('table.json', 'w') as f:
        #    w = csv.DictWriter(f, table[0].keys())
        #    w.writeheader()
        #    for line in table:
        #        w.writerow(line)

        print(table)  # parse as JSON
        print('clicked')
        return 'Sucesss', 200

@app.route('/ignore_json')
def ignore_json():
    
    return 'Sucesss', 200


@app.route('/showPDF')
def showPDF():
    

    return render_template('pdf.html')



if __name__ == '__main__':
    app.run(debug=True)