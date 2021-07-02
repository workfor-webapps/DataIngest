from Google import Create_Service, list_files
#import xlsxwriter

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

list_files(items) 