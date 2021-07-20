#from flask.globals import session
#from flask.helpers import flash, url_for
from src.drive_functions import Create_Service, get_files, get_temp_pdf
from src.Pdf_table_extr import extract_tables, get_title_from_pdf
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect, g, flash, url_for, session
import os

"""Main python file for flask application. This app uses google drive api to read and write data from
    a personal google account (needs to be changed to server maybe?). 
"""
class User:
    """This is a user class for storing user credential for logging in.
    
    :param id: Id for usres 
    :type id: int

    """
    def __init__(self, id , username, password) -> None:
        self.id = id
        self.username = username
        self.password = password
    def __repr__(self) -> str:
        return f'<user: {self.username}'

users = []
users.append(User(id=1, username='admin', password='admin'))

app = Flask(__name__)
app.secret_key = 'thisismysecretekey'

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']]
        g.user = user
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username and x.password == password]
        if user == []:
            flash ('Username or password incorrect. Please try agin!')
            return redirect(url_for('login'))
        else:
            session['user_id'] = user[0].id
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/')
def index():

    if not g.user:
        return redirect(url_for('login'))
            
    return render_template('index.html',pdf_list=[])

@app.route('/PullTables')  #  https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
def PullTable():
    """CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    files = get_files(service)
    file1 = files[0]
    file_id = file1["id"]
    get_temp_pdf(service, file_id)
    # path = os.getcwd() + "/temp/"
    temp_file = "/tmp/temp.pdf"
    paper_title = get_title(temp_file)
    doi = get_doi(temp_file)

    table_clean = extract_tables(temp_file)
    df = table_clean[1]
#
#     #-----------------Get json for table-------------
    #data = df.to_json(orient='table')
#     #------------------------------------------------
#
    html_file = df.to_html(index=False, justify="left", na_rep="", classes="table table-light table-striped table-hover table-bordered table-responsive-lg", table_id="pdf")
    text_file = open("./templates/table_temp1.html", "w")
    header = "{% extends 'table_base.html' %}\n{% block body %}"
    text_file.write(header)
    text_file.write(html_file)
    footer = "{% endblock %}"
    text_file.write(footer)
    text_file.close()"""
    paper_title = "Leadership Training Design, Delivery, and Implementation: A Meta-Analysis"
    doi = "10.1037/apl0000241"
    #paths = os.getcwd() + "/src/temp/Capture.PNG"
    table_num = request.args.get('table', default = 1, type = int)
    
    return render_template('indexT.html',table_num =table_num,  title=paper_title, DOI=doi)

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
        
        #return render_template('indexT.html', title="paper_title2")
        return 'Sucesss', 200

@app.route('/ignore_json')
def ignore_json():
    
    return 'Sucesss', 200


@app.route('/showPDF')
def showPDF():
    

    return render_template('pdf.html')



if __name__ == '__main__':
    app.run(debug=True)