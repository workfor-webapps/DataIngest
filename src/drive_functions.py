"""This is the google drive api module and contatins functions to interact to google drive

"""

import pickle
import os
import io
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request



def Create_Service(client_secret_file, api_name, api_version, *scopes):
    """Create a service connection to google drive

    :param client_secret_file: Client secret file generated from google api
    :type client_secret_file: json
    :param api_name: The api name for this aplication(drive)
    :type api_name: str
    :param api_version: version of the api(we are using version 3)
    :type api_version: str
    :return: service
    :rtype: api service
    """
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)


            cred = flow.run_local_server()
        
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def upload_files(service):
    """function to upload files to google drive through api call

    :param service: created google drive serviece
    :type service: API service
    """
    # authenticate account
    #service = get_gdrive_service()
    # folder details we want to make
    folder_metadata = {
        "name": "TestFolder",
        "mimeType": "application/vnd.google-apps.folder"
    }
    # create the folder
    file = service.files().create(body=folder_metadata, fields="id").execute()
    # get the folder id
    folder_id = file.get("id")
    print("Folder ID:", folder_id)
    # upload a file text file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": "test.txt",
        "parents": [folder_id]
    }
    # upload
    media = MediaFileUpload("test.txt", resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("File created, id:", file.get("id"))

def get_files(service):
    """A function to read files metadata from a folder (PDEA) in google drive
    to extract the tables

    :param service: google drive serviece
    :type service: service
    """
     

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
    return items

def get_temp_pdf(service, file_id):
    """This function downloads a file from google drive to a local machine
    using its file ID

    :param service: Google drive service
    :type service: service
    :param file_id: google drive file id
    :type file_id: str
    """


#list_files(items) 
#for item in items:
    # get the File ID
    #file_id = item["id"]
    # get the name of file
    #name = item["name"]

#file_id = '1UIaDlkEZBvH83i3VUs8CjjknPC8GYgGU'
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
