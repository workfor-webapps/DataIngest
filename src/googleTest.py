from Google import Create_Service, list_files
import io
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import tabula
import PyPDF2
import os
import pandas as pd
#import xlsxwriter

def google_t():
    CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    #file_metadata = {
    #    'name': 'PDEA',
    #    'mimeType': 'application/vnd.google-apps.folder'
    #}
    #service.files().create(body=file_metadata).execute()
    #print ('Folder ID: %s', file.get('id'))

    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'PDEA'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')

    # Now, using the folder ID gotten above, we get all the files from
    # that particular folder
    results = service.files().list(q = "'" + id + "' in parents", pageSize=10, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)").execute()
    items = results.get('files', [])

    #list_files(items) 
    file_id = '1UIaDlkEZBvH83i3VUs8CjjknPC8GYgGU'
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download: %", int(status.progress() * 100))

    fh.seek(0)

    with open('temp.pdf', 'wb') as f:
        f.write(fh.read())

    #3url = 'https://drive.google.com/file/d/1UIaDlkEZBvH83i3VUs8CjjknPC8GYgGU/view?usp=sharing'
    pdf_file = PyPDF2.PdfFileReader(fh)
    pages = pdf_file.numPages
    tables = tabula.read_pdf('temp.pdf', multiple_tables=True, pages='all')
    #print(pages)
    df = pd.DataFrame(tables[1])
    html = df.to_html()
    return html


    #print(tables[1])
if __name__ == '__main__':
    google_t()