"""This is the google drive api module and contatins functions to interact to google drive

"""
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload

def save_files(service, data, name, folderId, mimetype ):
    """function to upload files to google drive through api call

    :param service: created google drive serviece
    :type service: API service
    """
    # authenticate account
    #service = get_gdrive_service()
    # folder details we want to make
    #folder_metadata = {
    #    "name": "TestFolder",
    #    "mimeType": "application/vnd.google-apps.folder"
    #}
    # create the folder
    #file = service.files().create(body=folder_metadata, fields="id").execute()
    # get the folder id
    folder_id = folderId
    #print("Folder ID:", folder_id)
    # upload a file text file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": name,
        "parents": [folder_id]
    }
    # upload
    #string = " this is a test"
    #fh = bytes (data)#, encoding='utf8')
    #fd = BytesIO(data)
    media = MediaIoBaseUpload(data, mimetype=mimetype, chunksize=1024*1024, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    #print("File created, id:", file.get("id"))
    fileId = file.get("id")
    fileUrl = file.get("webViewLink")
    return fileId, fileUrl

def get_archive_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'Archive'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_NoDOI_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'NoDOI'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_Images_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'Images'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_JsonTables_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'JsonTable'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_New_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'New'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_logs_folder_id(service):
    
    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'logs'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')
    return id

def get_files(service, folder_id):
    """A function to read files metadata from a folder (PDEA) in google drive
    to extract the tables

    :param service: google drive serviece
    :type service: service
    """
    
    id = folder_id

    # Now, using the folder ID gotten above, we get all the files from
    # that particular folder
    results = service.files().list(q = "'" + id + "' in parents", orderBy = "createdTime desc", pageSize=10, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, webContentLink, webViewLink )").execute()

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


def move_file(service, file_id, folder_id):

    # Retrieve the existing parents to remove
    file = service.files().get(fileId=file_id,
                                    fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    # Move the file to the new folder
    file = service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()


#list_files(items) 
#for item in items:
    # get the File ID
    #file_id = item["id"]
    # get the name of file
    #name = item["name"]

#file_id = '1UIaDlkEZBvH83i3VUs8CjjknPC8GYgGU'
    #request = service.files().get_media(fileId=file_id)
    #fh = io.BytesIO()
    #downloader = MediaIoBaseDownload(fh, request)
    #done = False
    #while done is False:
    #    status, done = downloader.next_chunk()
    #    print ("Download: %", int(status.progress() * 100))

    #fh.seek(0)
    
    
    #with open('temp.pdf', 'wb') as f:
    #    f.write(fh.read()) 
    
