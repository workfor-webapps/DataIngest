"""Main python file for flask application. This app uses google drive api to read and write data from
    a personal google account (needs to be changed to server maybe?). 
"""
from src.drive_functions import *
from src.Pdf_table_extr import *
from flask import Flask, render_template, request, redirect, g, flash, url_for, session, render_template_string
import os, sys, io, json, re
import datetime
import logging
import PyPDF2
import pandas as pd
#import google.oauth2.credentials
import google_auth_oauthlib.flow
#import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseDownload
import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()
handler = client.get_default_handler()
#handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
client.setup_logging()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES  = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
API_SERVICE_DRIVE = 'drive'
API_SERVICE_SHEET = 'sheets'
API_DRIVE_VERSION = 'v3'
API_SHEET_VERSION = 'v4'
SPREADSHEETID = "1PyzArReUyKQAnYbBWkMDzUjNSw194HmckzCkmjt9_3A"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class User:
    """This is a class to store user credentials to login.
    
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

#add admin user
users = []
users.append(User(id=1, username='admin', password='admin'))
users.append(User(id=2, username='user1', password='user1'))


app = Flask(__name__)
app.secret_key = 'thisismysecretekey'

#------------------------------------------------------------------------------------------------
@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']]
        g.user = user
    
#------------------------------------------------------------------------------------------------
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
            logger.info('User with ID:%s logged in'%(user[0].id))
            return redirect(url_for('index'))
    
    return render_template('login.html')

#------------------------------------------------------------------------------------------------
@app.route('/')
def index():

    if not g.user:
        return redirect(url_for('login'))
    
    if 'credentials' not in session:
        return redirect('authorize')

    else:
        return redirect(url_for('list'))  

#------------------------------------------------------------------------------------------------
@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        approval_prompt='force',
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)

#-------------------------------------------------------------------------------------------------
@app.route('/oauth2callback')
def oauth2callback():
    
    state = session['state']
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    dict = credentials_to_dict(credentials)
    store_cred(dict)
    session['credentials'] = dict
    
    logger.info('UserID %s has been authorized access to API' %(session['user_id']) )

    return redirect(url_for('list'))

#------------------------------------------------------------------------------------------------
#  https://www.python.org/dev/peps/pep-0008/#function-and-variable-names
@app.route('/PullTables')
def PullTable():

    header = "{% extends 'table_base.html' %}\n{% block body %}\n"
    footer = "\n{% endblock %}"

    drive = get_service(API_SERVICE_DRIVE, API_DRIVE_VERSION)
    file_items = get_files(drive, get_folder_id(drive, "Json"))  

    if not file_items:
        flash ('No table for extraction!')
        logger.info('No table is ready for extraction by %s' %(session['user_id']))
        return redirect(url_for('index'))

    requested = drive.files().get_media(fileId=file_items[0]["id"])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, requested)
    done = False

    while done is False:
            status, done = downloader.next_chunk()
    
    fh.seek(0)
    extracted_data = json.load(fh)
    

    pub = []
    for data in extracted_data:
        pub.append(PubData(data["doi"]))
        
    paper = request.args.get("paper" , default = 0, type = int)
    table_num = request.args.get("table_num" , default = 0, type = int)


    if paper >= len(extracted_data) :
        empty_Images_folder(drive)
        
        #saving new log file
        log_file = []

        for data_f in extracted_data:
            files_data = dict.fromkeys(['name', 'doi', 'status'])
            files_data["doi"] = data_f["doi"]
            files_data["name"] = data_f["name"]
            files_data["status"] = "Processed"
            log_file.append(files_data)
            #print(log_file)
        
        # convert logs into JSON:
        data_j = json.dumps(log_file)
        folderId = get_folder_id(drive, "Logs")
        json_byte = io.BytesIO(bytes(data_j, encoding='utf8'))
        name = datetime.datetime.now().strftime("%Y%m%d%H")
        save_files(service=drive, data=json_byte, name=name, folderId=folderId, mimetype="application/json")    # convert logs into JSON:

        move_file(service=drive, file_id=file_items[0]["id"],folder_id=get_folder_id(drive, "PDFcomplete"))
        flash ('Table processing complete!')
        return redirect(url_for('index'))
    
    logger.info('Table %s from paper with DOI: %s is being processed by userID %s' %(table_num, extracted_data[paper]["doi"] , session['user_id']))

    table_html = extracted_data[paper]["tables"][table_num] 
    table_html = header + table_html + footer 
    rendered_table =  render_template_string(table_html)
    page =  extracted_data[paper]["pages_urls"][table_num]
    page = re.sub("/view?.*", "/preview", page)

    PDFurl =  extracted_data[paper]["PDF_url"]
    PDFurl = re.sub("/view?.*", "/preview", PDFurl)

    pub_data = pub[paper]
    max_tables = len(extracted_data[paper]["tables"])
     
    return render_template('indexT.html',table_num = table_num, tables = page, 
                            table_html= rendered_table , pub_data = pub_data, 
                            max_tables = max_tables, pdf_url = PDFurl)

#------------------------------------------------------------------------------------------------
@app.route('/extract')
def extract():
 
    drive = get_service(API_SERVICE_DRIVE, API_DRIVE_VERSION)

    #get files metadata in PDEA folder on google drive
    folder_id = get_folder_id(drive, "PDFqueue")
    file_items = get_files(drive, folder_id)
    
    log_file = []
    data_file = []

    if not file_items:
        return redirect(url_for('list'))



    for file in file_items:
        files_data = dict.fromkeys(['name', 'doi', 'pages', 'PDF_url','pages_urls', 'tables'])
        files_log = dict.fromkeys(['name', 'doi', 'status'])
        
        files_data["PDF_url"] = file["webViewLink"]
        files_data["name"] = file["name"]
        files_log["name"] = file["name"]     

        request = drive.files().get_media(fileId=file["id"])

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while done is False:
            status, done = downloader.next_chunk()

        fh.seek(0)
        doi = get_doi(fh)
        files_data["doi"] = doi
        files_log["doi"] = doi

        if doi == "DOI not found!": # move to "nodoi" folder"
            file_id = file["id"]
            folder_id = get_folder_id(drive, "PDFreview")
            logger.info('DOI not found in one PDF. Moved to PDFreview folder')
            move_file(service=drive, file_id=file_id,folder_id=folder_id)
            files_log["status"] = "Failed"
        else:
            state = store_doi(doi)
            #state = "New"
            logger.info('Extracting DOI: %s' %doi)

            if state == "Old":
                logger.info('DOI: %s is already in database' %doi)
                file_id = file["id"]
                folder_id = get_folder_id(drive, "PDFComplete")
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

                logger.info('%s tables are extracted from DOI: %s' %(len(tables), doi))
                print(pages)
                # get and save pages
                pages_url = []
                for page in pages:
                    pdf_file = PyPDF2.PdfFileReader(fh)
                    pdf_page = pdf_file.getPage(page[0]-1)
                    
                    if page[1]: # if rotated page
                         pdf_page.rotateClockwise(90)

                    pdf_writer = PyPDF2.PdfFileWriter()
                    pdf_writer.addPage(pdf_page)
                    pdf_page_bytes = io.BytesIO()
                    pdf_writer.write(pdf_page_bytes)

                    #save pdf pages to images folder
                    folderId = get_folder_id(drive, "PDF_PageImage")
                    P_id, P_url = save_files(service=drive, data=pdf_page_bytes, 
                                            name=doi+str(page[0]), folderId= folderId, 
                                            mimetype = "application/pdf")
                    #P_url = re.sub("/view?*", "/preview", P_url) 
                    pages_url.append(P_url)
                
                files_data["pages_urls"] = pages_url

                folder_id = get_folder_id(drive, "PDFComplete")
                move_file(service=drive, file_id=file["id"],folder_id=folder_id)


        #saveing log and table dat for all files in a batch
        log_file.append(files_log)
        data_file.append(files_data)

    # convert logs into JSON:
    data = json.dumps(log_file)
    folderId = get_folder_id(drive, "Logs")
    json_byte = io.BytesIO(bytes(data, encoding='utf8'))
    name = datetime.datetime.now().strftime("%Y%m%d%H")
    save_files(service=drive, data=json_byte, name=name, folderId=folderId, mimetype="application/json")

    # convert tables into JSON:
    data = json.dumps(data_file)
    folderId = get_folder_id(drive, "Json")
    json_byte = io.BytesIO(bytes(data, encoding='utf8'))
    name = datetime.datetime.now().strftime("%Y%m%d%H") 
    save_files(service=drive, data=json_byte, name=name, folderId=folderId, mimetype="application/json")
    fh.flush()  

    return redirect(url_for('list'))

#------------------------------------------------------------------------------------------------
@app.route('/status_update')
def list():

    drive = get_service(API_SERVICE_DRIVE, API_DRIVE_VERSION)
    
     #get files metadata in PDEA folder on google drive
    file_items = get_files(drive, get_folder_id(drive, "Logs"))

    if (file_items == 0) or (not file_items):
         file_num = 0
         logs = {"name":"-","doi":"-","status":"-"}
    else:

        request = drive.files().get_media(fileId=file_items[0]["id"])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
                status, done = downloader.next_chunk()

        fh.seek(0)
        logs = json.load(fh)  
        file_num = len(logs)
        fh.flush()

    return render_template('index.html', files_data=logs, file_numbers = file_num)
    
#------------------------------------------------------------------------------------------------
@app.route('/post_json', methods = ['POST'])
def post_json():

    if request.method == 'POST':

        drive = get_service(API_SERVICE_SHEET, API_SHEET_VERSION)
        sheet = drive.spreadsheets()

        #get the column name order
        first_row = sheet.values().get(spreadsheetId=SPREADSHEETID, range="Sheet1!A1:AA1", majorDimension="ROWS").execute()
        sheet_row = first_row.get('values',[])[0]
        

        rec_data = request.form
        table = json.loads(rec_data["table"])

        df = pd.DataFrame(table)
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)

        for column in df.columns:
            if df.loc[0,column]=="":
                df.drop(columns=column, inplace=True)
        df = df.rename(columns=df.iloc[0,0:])
        df = df.drop([0])
        df.columns = df.columns.str.upper()
        
        df["ThemeA"] = rec_data["Ref_Con"]
        df["ConceptA"] = rec_data["Con_Cat"]
        df["ConceptADirection"] = rec_data["Con_Dir"]
        df["EffectType"] = rec_data["Eff_Type"]
        df["DOI"] = rec_data["DOI"]
        df["TableID"] = str(int(rec_data["Table_num"]) + 1)
        df["Citation"] = get_citation(rec_data["DOI"])
        if "META-ANALYSIS" in df.columns:
            df["ConceptB"] = df["META-ANALYSIS"]
            df = df.drop(["META-ANALYSIS"], axis=1)
        else:
            df["ConceptB"] = " "

        df["ThemeB"] = df["CONCEPT THEME"] #?
        df = df.drop(["CONCEPT THEME"], axis=1)

        sheet_row_upper = [str(x).upper() for x in sheet_row]
        list_col_upper = df.columns.str.upper().tolist()
        list_col =  df.columns.tolist()

        append_list = [x for x in list_col if str(x).upper() not in sheet_row_upper]
        append_list_upper = [str(x).upper() for x in append_list]

        #add spreadsheet columns to dataframe if not already there 
        for col_n in sheet_row:
            if col_n.upper() not in list_col_upper:
                df[col_n] = " "
        
        #make all columns uppercase
        df.columns = df.columns.str.upper()

        #order the columns
        list_ordered = sheet_row_upper + append_list_upper
        df = df[list_ordered]
        
        #drop column names
        df = df.rename(columns=df.iloc[0,0:])
        df.drop(index=df.index[0], axis=0, inplace=True)

        new_sheet_row = sheet_row + append_list

        #extend the new column values
        body = dict(majorDimension='ROWS', values = [new_sheet_row])
        response1 = sheet.values().update(
            valueInputOption='USER_ENTERED', spreadsheetId=SPREADSHEETID, range="Sheet1!A1:AA1",
            body=body).execute()


        body = dict(majorDimension='ROWS', values = df.T.reset_index().T.values.tolist())
        response = sheet.values().append(
            valueInputOption='USER_ENTERED', spreadsheetId=SPREADSHEETID, range="Sheet1!A2",
            body=body).execute()
        
        logger.info("Table %s from DOI: %s is added to the spreadsheet by userID %s" %(rec_data["Table_num"], rec_data["DOI"], session["user_id"] ))

        return 200

@app.route('/ignore_json', methods = ['POST'])
def ignore_json():
    if request.method == 'POST':

        rec_data = request.form
        logger.info("Table %s from DOI: %s is ignored by userID %s" %(rec_data["Table_num"], rec_data["DOI"], session["user_id"] ))

    return 200


#------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(debug=True,host='0.0.0.0', port=8080)
    app.run(debug=True,host='localhost', port=8080)