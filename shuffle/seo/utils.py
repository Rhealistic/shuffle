import os
import requests

from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as AccountCredentials

API_KEY_FILE = "your-api-key.json"
URL_TO_INDEX = "https://example.com/page-to-index"

def get_google_indexing_credentials(api_key_file):
    if os.path.exists(api_key_file):
        return AccountCredentials.from_service_account_file(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), api_key_file), 
            scopes=["https://www.googleapis.com/auth/indexing"]
        )

    return Credentials.from_authorized_user_file(
        "authorized_user.json", scopes=["https://www.googleapis.com/auth/indexing"]
    )

def notify_google_indexing(site, url_to_index):
    try:
        credentials = get_google_indexing_credentials("api_key_file")

        # Create a session and set up the credentials
        session = requests.Session()
        session.auth = credentials

        # URL for indexing request
        indexing_url = "https://indexing.googleapis.com/v3/urlNotifications:publish"

        # Request payload
        request_data = {
            "urlNotification": {
                "url": url_to_index,
                "type": "URL_UPDATED"
            }
        }

        response = session.post(indexing_url, json=request_data)

        if response.status_code == 200:
            print(f"Indexing request for {url_to_index} sent successfully.")
        else:
            print(f"Failed to send indexing request. Status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

