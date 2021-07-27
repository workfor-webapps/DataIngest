"""Main python file for flask application. This app uses google drive api to read and write data from
    a personal google account (needs to be changed to server maybe?). 
"""

from src.drive_functions import get_new_files, get_NoDOI_folder_id, move_file, get_archive_folder_id
from src.Pdf_table_extr import PubData, extract_tables, get_doi, get_title_from_pdf
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect, g, flash, url_for, session, jsonify
import os, sys, io
import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
#from google.cloud import datastore

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES  = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class User:
    """This is a class to store user credentials for loging in
    
    :param id: User id 
    :type id: int
    :param username: username
    :type username: str
    :param password: password
    :type password: str
    
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
    
    if 'credentials' not in session:
        return redirect('authorize')

    else:

        return render_template('index.html',pdf_list=[])
    


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)


    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    
    state = session['state']
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)
 	
    credentials = flow.credentials
    print(credentials)
    store_cred(credentials_to_dict(credentials))

    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('list'))

@app.route('/PullTables')  #  https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
def PullTable():
    """

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


@app.route('/extract')
def extract():
    
    
    credential = get_cred()
    session['credentials'] = credentials_to_dict(credential)

    #print(credential)
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    store_cred (credentials_to_dict(credentials))
    session['credentials'] = credentials_to_dict(credentials)

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    #get files metadata in PDEA folder on google drive
    file_items = get_new_files(drive)
    
    #initialize files dict
    #files_data = dict.fromkeys(['name', 'doi', 'status'])

    #file_name = []
    #file_doi = []
    #file_status = []
    if not file_items:
        return 'No new file', 200

    for file in file_items:
        #1. download the file 
        request = drive.files().get_media(fileId=file["id"])

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while done is False:
            status, done = downloader.next_chunk()
            #print ("Download: %", int(status.progress() * 100))

        doi = get_doi(fh)

        if doi == "DOI not found!": # move to "nodoi" folder"
            file_id = file["id"]
            folder_id = get_NoDOI_folder_id(drive)
            move_file(service=drive, file_id=file_id,folder_id=folder_id)
        else:
            state = store_doi(doi)
            
            if state == "Old":
                file_id = file["id"]
                folder_id = get_archive_folder_id(drive)
                move_file(service=drive, file_id=file_id,folder_id=folder_id)
            else:
                # here extract and save table data
                pass




        


    #df = tabula.read_pdf(files[0]["webContentLink"], pages='all')
    #print(df[0])
    return 'Sucesss', 200


@app.route('/status_update')
def list():



    return render_template('index.html', files_data=files_data, file_numbers = len(file_items))
    




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


def store_cred(credentials):
    datastore_client = datastore.Client(project="metadata-pdea")
    kind = 'drive_cred'
    id = 5644004762845184 
    key = datastore_client.key(kind, id)
    entity = datastore.Entity(key=key)
    entity.update({
        'token': credentials["token"],
        'refresh_token': credentials["refresh_token"],
        'token_uri': credentials["token_uri"],
        'client_id': credentials["client_id"],
        'client_secret': credentials["client_secret"],
        'scopes': credentials["scopes"]})

    datastore_client.put(entity)

def store_doi(doi, url):
    datastore_client = datastore.Client(project="metadata-pdea")
    
    #check if doi already exist
    query = datastore_client.query(kind="files")
    query.add_filter("doi", "=", doi)
    results = list(query.fetch())

    if not results:
        status = "New"
        # Create an incomplete key for an entity of kind "Task". An incomplete
        # key is one where Datastore will automatically generate an Id
        key = datastore_client.key("files")
        entity = datastore.Entity(key=key)
        entity.update(
            {
                "doi": doi,
                "url": url,
                "status": status,
            }
        )
        
        datastore_client.put(entity)
    
    else:
        status = "Old"

    return status




def get_cred():
    datastore_client = datastore.Client(project="metadata-pdea")
    kind = 'drive_cred'
    id = 5644004762845184 
    key = datastore_client.key(kind, id)
    cred = datastore_client.get(key=key)
      
    return cred

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8888)