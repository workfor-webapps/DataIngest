"""This is the google drive api module and contatins functions to interact to googledrive
    and googlesheets
"""

from io import BytesIO
from flask import session, redirect
from google.cloud import datastore
import google.oauth2.credentials
import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseUpload

#-----------------------------------------------------------------------------------------
def store_cred(credentials):

    """This function is for saving credentials to a persistent datastore- no return value

    :param credentials: google drive credentials
    :type credentials: dictionary
    """
    datastore_client = datastore.Client()
    #Id for cred entity in datastore
    kind = 'drive_cred'
    id = 5634161670881280 
    with datastore_client.transaction():
        key = datastore_client.key(kind, id)
        entity = datastore_client.get(key=key)
        entity["token"] = credentials["token"]
        #entity["refresh_token"] = credentials["refresh_token"]
        #entity["token_uri"] = credentials["token_uri"]
        #entity["client_id"] = credentials["client_id"]
        #entity["client_secret"] = credentials["client_secret"]
        #entity["scopes"] = credentials["scopes"]
        datastore_client.put(entity)

#-----------------------------------------------------------------------------------------
def get_cred():

    """This function is for retrieving exicting credentials from the datastore

    :return: credentials
    :rtype: dictionary
    """
    datastore_client = datastore.Client()
    kind = 'drive_cred'
    id = 5634161670881280 
    key = datastore_client.key(kind, id)
    credentials = datastore_client.get(key=key)
      
    return credentials

#-----------------------------------------------------------------------------------------
def store_doi(doi):
    """This function saves the doi in the datastore if it does not exist already. If doi is already in 
    the databse, returns 'old' status. 

    :param doi: publication DOI
    :type doi: str
    :return: status
    :rtype: str
    """
    datastore_client = datastore.Client()
    #check if doi already exist
    query = datastore_client.query(kind="files")
    query.add_filter("doi", "=", doi)
    results = list(query.fetch())

    if not results:
        status = "New"
        key = datastore_client.key("files")
        entity = datastore.Entity(key=key)
        entity.update({"doi": doi,})
        datastore_client.put(entity)
    
    else:
        status = "Old"

    return status

#-----------------------------------------------------------------------------------------
def credentials_to_dict(credentials):
    """This function gets credentials object and returns a dict object.

    :param credentials: google drive credentials
    :type credentials: credentials
    :return: dictionary object
    :rtype: dict
    """
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

#-----------------------------------------------------------------------------------------
def get_service(API_SERVICE_NAME, API_VERSION):
    """This function builds and returns google drive/sheets service

    :param API_SERVICE_NAME: name of the requested service
    :type API_SERVICE_NAME: str
    :param API_VERSION: API version to use
    :type API_VERSION: str
    :return: google service object
    :rtype: google service
    """

    credential = get_cred()
    session['credentials'] = credential

    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    
    Dict_cred = credentials_to_dict(credentials)
    store_cred (Dict_cred)
    session['credentials'] = Dict_cred

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    return service

#-----------------------------------------------------------------------------------------
def save_files(service, data, name, folderId, mimetype ):
    """This function is to upload files to connected google drive

    :param service: google drive service 
    :type service: google service
    :param data: IO data to be saved 
    :type data: BytesIO
    :param name: name of the file to save the data into
    :type name: str
    :param folderId: Drive folder Id to save the data into
    :type folderId: str
    :param mimetype: minetype of the file
    :type mimetype: str
    :return: saved file Id and url
    :rtype: str
    """

    folder_id = folderId
    file_metadata = {
        "name": name,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(data, mimetype=mimetype, chunksize=1024*1024, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    fileId = file.get("id")
    fileUrl = file.get("webViewLink")
    
    return fileId, fileUrl

#-----------------------------------------------------------------------------------------
def get_folder_id(service, name):
    """This function gets the folder ID with a given name in the connected google drive.

    :param service: google drive service object
    :type service: service
    :param name: folder name
    :type name: str
    :return: folder ID
    :rtype: str
    """
    
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains " + "'" + name + "'",
     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folderIdResult = folderId.get('files', [])
    if not folderIdResult: return 0
    #we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

#-----------------------------------------------------------------------------------------
def get_files(service, folder_id):
    """This funtion finds all the files in a google drive folder and returns their metadata.

    :param service: google drive service object
    :type service: service
    :param folder_id: google drive folder ID (obtainable from ''get_folder_id(service, name)'' function)
    :type folder_id: str
    :return: list of files metadata in the google folder
    :rtype: list
    """
    
    id = folder_id
    if id == 0: return 0

    results = service.files().list(
        q = "'" + id + "' in parents", 
        orderBy = "createdTime desc", 
        pageSize=10, 
        fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, webContentLink, webViewLink )"
        ).execute()

    items = results.get('files', [])

    return items

def find_file(service, folder_id, file_name):
    """This funtion finds a specific files in a google drive folder and returns their metadata.

    :param service: google drive service object
    :type service: service
    :param folder_id: google drive folder ID (obtainable from ''get_folder_id(service, name)'' function)
    :type folder_id: str
    :return: list of files metadata in the google folder
    :rtype: list
    """
    
    id = folder_id
    if id == 0: return 0

    results = service.files().list(
        q = "'" + id + "' in parents and name='"+file_name+"'", 
        orderBy = "createdTime desc", 
        pageSize=10, 
        fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, webContentLink, webViewLink )"
        ).execute()

    items = results.get('files', [])

    return items

#-----------------------------------------------------------------------------------------
def move_file(service, file_id, folder_id):
    """This function moves the given file with the ''file_id'' to the folder with ''folder_id''.

    :param service: google drive service object
    :type service: service
    :param file_id: Id of the file to be moved
    :type file_id: str
    :param folder_id: Google drive folder ID to move the file into
    :type folder_id: str
    """

    # Retrieve the existing parents to remove
    file = service.files().get(fileId=file_id,
                                    fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    # Move the file to the new folder
    file = service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()

def remove_file(service, file_Id):
    """This function removes a file with a file ID. No return value

    :param service: google drive service object
    :type service: service
    :param file_Id: file ID
    :type service: str
    """
    
    service.files().delete(fileId=file_Id).execute()

#-----------------------------------------------------------------------------------------
def empty_Images_folder(service, doi):
    """This function removes all the files for a doi in Images folder. No return value

    :param service: google drive service object
    :type service: service
    :param doi: DOI
    type doi: str
    """
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'PDF_PageImage'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folderIdResult = folderId.get('files', [])
    id = folderIdResult[0].get('id')
    results = service.files().list(q = "'" + id + "' in parents and name contains '" + doi + "'", orderBy = "createdTime desc", pageSize=10, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, webContentLink, webViewLink )").execute()
    items = results.get('files', [])

    for item in items:
        service.files().delete(fileId=item["id"]).execute()

