from drive_functions import Create_Service, get_files

CLIENT_SECRET_FILE = 'client_secret_1069569447-dopmb5ed801nq4ovfvla6ba4pa3k5217.apps.googleusercontent.com.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
file_ids = get_files(service)


