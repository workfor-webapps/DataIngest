from google.cloud import secretmanager

PROJECT_ID = "dataingest-26020"
def create_secret(secret_id):
    #Call the function to create a new secret called my_secret_value:
    #create_secret("my_secret_value")

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the parent project.
    parent = f"projects/{PROJECT_ID}"

    # Build a dict of settings for the secret
    secret = {'replication': {'automatic': {}}}

    # Create the secret
    response = client.create_secret(secret_id=secret_id, parent=parent, secret=secret)

    # Print the new secret name.
    print(f'Created secret: {response.name}')  


def add_secret_version(secret_id, payload):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the parent secret.
    parent = f"projects/{PROJECT_ID}/secrets/{secret_id}"

    # Convert the string payload into a bytes. This step can be omitted if you
    # pass in bytes instead of a str for the payload argument.
    payload = payload.encode('UTF-8')

    # Add the secret version.
    response = client.add_secret_version(parent=parent, payload={'data': payload})

    # Print the new secret version name.
    print(f'Added secret version: {response.name}')   

# Call the function to create a add a new secret version:

# add_secret_version("my_secret_value", "Hello Secret Manager")

def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')
