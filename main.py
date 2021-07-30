"""Main python file for flask application. This app uses google drive api to read and write data from
    a personal google account (needs to be changed to server maybe?). 
"""
import mock
from werkzeug.utils import html
from werkzeug.datastructures import ImmutableMultiDict
from src.drive_functions import get_New_folder_id, get_files, get_NoDOI_folder_id, get_logs_folder_id, move_file, \
                                get_archive_folder_id, save_files, get_Images_folder_id, get_JsonTables_folder_id

from src.Pdf_table_extr import PubData, extract_tables, get_doi
#from google.cloud import datastore
from flask import Flask, render_template, request, redirect, g, flash, url_for, session, jsonify, render_template_string
import os, sys, io, json, re
import pickle, PyPDF2, tabula
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import datetime
from google.cloud import datastore


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

        files_data = dict.fromkeys(['name', 'doi', 'status'])
        files = [files_data]

        return render_template('index.html', files_data=files,file_numbers = 1)
    


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


    # html_file = df.to_html(index=False, justify="left", na_rep="", classes="table table-light table-striped table-hover table-bordered table-responsive-lg", table_id="pdf")
    header = "{% extends 'table_base.html' %}\n{% block body %}\n"
    footer = "\n{% endblock %}"

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    #store_cred (credentials_to_dict(credentials))
    session['credentials'] = credentials_to_dict(credentials)

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    #get files metadata in PDEA folder on google drive
    file_items = get_files(drive, get_JsonTables_folder_id(drive))  

    if not file_items:
        return "No table is ready for extraction"

    requested = drive.files().get_media(fileId=file_items[0]["id"])

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, requested)
    done = False
    while done is False:
            status, done = downloader.next_chunk()
            #print ("Download: %", int(status.progress() * 100))
    fh.seek(0)
    extracted_data = json.load(fh)

    
    pub = []
    for data in extracted_data:
        pub.append(PubData(data["doi"]))
        
    paper = request.args.get("paper" , default = 0, type = int)
    table_num = request.args.get("table_num" , default = 0, type = int)

    if paper >= len(extracted_data) :
        return "success" , 200

    table_html = extracted_data[paper]["tables"][table_num] 
    table_html = header + table_html + footer 
    rendered_table =  render_template_string(table_html)
    page =  extracted_data[paper]["pages_urls"][table_num]
    page = re.sub("/view?.*", "/preview", page)

    pub_data = pub[paper]

    max_tables = len(extracted_data[paper]["tables"])
     
    
    return render_template('indexT.html',table_num = table_num, tables = page, table_html= rendered_table , pub_data = pub_data, max_tables = max_tables)


@app.route('/extract')
def extract():
    
    
    #credential = get_cred()
    #session['credentials'] = credentials_to_dict(credential)

    #print(credential)
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    #store_cred (credentials_to_dict(credentials))
    session['credentials'] = credentials_to_dict(credentials)

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    #get files metadata in PDEA folder on google drive
    folder_id = get_New_folder_id(drive)
    file_items = get_files(drive, folder_id)
    
    log_file = []
    data_file = []

    #initialize files dict
    #files_data = dict.fromkeys(['name', 'doi', 'pages', 'PDF_url','pages_urls', 'tables'])
    #files_log = dict.fromkeys(['name', 'doi', 'status'])

    if not file_items:
        return 'No new file', 200

    for file in file_items:
        files_data = dict.fromkeys(['name', 'doi', 'pages', 'PDF_url','pages_urls', 'tables'])
        files_log = dict.fromkeys(['name', 'doi', 'status'])
        
        files_data["PDF_url"] = file["webViewLink"]
        files_data["name"] = file["name"]
        files_log["name"] = file["name"]
        #1. download the file 
        request = drive.files().get_media(fileId=file["id"])

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        
        
        while done is False:
            status, done = downloader.next_chunk()
            #print ("Download: %", int(status.progress() * 100))
        fh.seek(0)
        doi = get_doi(fh)
        files_data["doi"] = doi
        files_log["doi"] = doi
        
        if doi == "DOI not found!": # move to "nodoi" folder"
            file_id = file["id"]
            folder_id = get_NoDOI_folder_id(drive)
            move_file(service=drive, file_id=file_id,folder_id=folder_id)
            files_log["status"] = "Failed"
        else:
            #state = store_doi(doi)
            state = "New"
            
            if state == "Old":
                file_id = file["id"]
                folder_id = get_archive_folder_id(drive)
                move_file(service=drive, file_id=file_id,folder_id=folder_id)
                files_data["status"] = "Duplicate"
                files_log["status"] = "Duplicated"
            else:
                # here extract and save table data
                tables, pages = extract_tables(fh)
                files_data["tables"] = tables
                files_data["pages"] = pages
                files_data["status"] = "Ready"
                files_log["status"] = "Ready"

                # get and save pages
                pages_url = []
                for page in pages:
                    pdf_file = PyPDF2.PdfFileReader(fh)
                    pdf_page = pdf_file.getPage(page-1)
                    pdf_writer = PyPDF2.PdfFileWriter()
                    pdf_writer.addPage(pdf_page)
                    pdf_page_bytes = io.BytesIO()
                    pdf_writer.write(pdf_page_bytes)

                    #save pdf pages to images folder
                    folderId = get_Images_folder_id(drive)
                    P_id, P_url = save_files(service=drive, data=pdf_page_bytes, name=doi+str(page), folderId= folderId, mimetype = "application/pdf" )
                    P_url = re.sub("/view?*", "/preview", P_url)
                    pages_url.append(P_url)
                
                files_data["pages_urls"] = pages_url

                folder_id = get_archive_folder_id(drive)
                move_file(service=drive, file_id=file["id"],folder_id=folder_id)


        #saveing log and table dat for all files in a batch
        log_file.append(files_log)
        data_file.append(files_data)


    # convert logs into JSON:
    data = json.dumps(log_file)
    folderId = get_logs_folder_id(drive)
    json_byte = io.BytesIO(bytes(data, encoding='utf8'))
    name = datetime.datetime.now().strftime("%Y%m%d%H")
    save_files(service=drive, data=json_byte, name=name, folderId=folderId, mimetype="application/json")

    # convert tables into JSON:
    data = json.dumps(data_file)
    folderId = get_JsonTables_folder_id(drive)
    json_byte = io.BytesIO(bytes(data, encoding='utf8'))
    name = datetime.datetime.now().strftime("%Y%m%d%H") 
    save_files(service=drive, data=json_byte, name=name, folderId=folderId, mimetype="application/json")

    fh.flush()  

    return 'Sucesss', 200

@app.route('/status_update')
def list():

    #credential = get_cred()
    #session['credentials'] = credentials_to_dict(credential)

    #print(credential)
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    #store_cred (credentials_to_dict(credentials))
    session['credentials'] = credentials_to_dict(credentials)

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
     #get files metadata in PDEA folder on google drive
    file_items = get_files(drive, get_logs_folder_id(drive))
    

    request = drive.files().get_media(fileId=file_items[0]["id"])

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
            status, done = downloader.next_chunk()
            #print ("Download: %", int(status.progress() * 100))
    fh.seek(0)
    logs = json.load(fh)
    print(logs)
    print(file_items[0]["name"])
    file_num = len(logs)
    fh.flush()

    return render_template('index.html', files_data=logs, file_numbers = file_num)
    




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

        #print(table)  # parse as JSON
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
    db_credentials = mock.Mock(spec=google.oauth2.credentials.Credentials)
    #db = ndb.Client(project="test", credentials=credentials)
    datastore_client = datastore.Client(project="metadata-pdea", credentials=db_credentials)
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

def store_doi(doi):
    #datastore_client = datastore.Client(project="metadata-pdea")
    db_credentials = mock.Mock(spec=google.oauth2.credentials.Credentials)
    #db = ndb.Client(project="test", credentials=credentials)
    datastore_client = datastore.Client(project="metadata-pdea", credentials=db_credentials)
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
            }
        )
        
        datastore_client.put(entity)
    
    else:
        status = "Old"

    return status




def get_cred():
    #datastore_client = datastore.Client(project="metadata-pdea")
    db_credentials = mock.Mock(spec=google.oauth2.credentials.Credentials)
    #db = ndb.Client(project="test", credentials=credentials)
    datastore_client = datastore.Client(project="metadata-pdea", credentials=db_credentials)
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
    app.run(debug=True, host='localhost', port=8080)