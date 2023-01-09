from google.cloud import secretmanager

def get_secret(secret_id):

    # Create a client
    client = secretmanager.SecretManagerServiceClient()

    # Retrieve a secret
    secret_name = f'projects/758823822100/secrets/{secret_id}/versions/latest'
    secret = client.access_secret_version(request={"name": secret_name})
    maps_api_key = secret.payload.data.decode('utf-8')

    return maps_api_key
