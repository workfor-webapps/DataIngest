"""This is the google drive api module and contatins functions to interact to google drive

"""

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
    #media = MediaFileUpload("test.txt", resumable=True)
    #file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("File created, id:", file.get("id"))

def get_new_files(service):
    """A function to read files metadata from a folder (PDEA) in google drive
    to extract the tables

    :param service: google drive serviece
    :type service: service
    """
     

    # First, get the folder ID by querying by mimeType and name
    folderId = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name contains 'New'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # this gives us a list of all folders with that name
    folderIdResult = folderId.get('files', [])
    # however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
    id = folderIdResult[0].get('id')

    # Now, using the folder ID gotten above, we get all the files from
    # that particular folder
    results = service.files().list(q = "'" + id + "' in parents", pageSize=10, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime, webContentLink, webViewLink )").execute()
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
    
