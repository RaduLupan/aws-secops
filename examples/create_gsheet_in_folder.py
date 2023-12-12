from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

def create_google_sheet(service_account_key_path, folder_id, sheet_name):
    """
    Creates a new Google Sheet in the specified folder using the provided service account key.

    Args:
        service_account_key_path (str): The path to the service account key file.
        folder_id (str): The ID of the folder where the Google Sheet will be created.
        sheet_name (str): The name of the new Google Sheet.

    Returns:
        str: The ID of the created Google Sheet, or None if an error occurred.
    """
    # Load the credentials from the service account key file
    credentials = service_account.Credentials.from_service_account_file(service_account_key_path,
                                                                         scopes=['https://www.googleapis.com/auth/drive'])
    # Create a Google Drive API client
    drive_service = build('drive', 'v3', credentials=credentials)

    # Check if the specified folder_id exists
    folder_exists = drive_service.files().get(fileId=folder_id).execute()

    if not folder_exists:
        print(f"Folder with ID {folder_id} not found.")
        return None

    # Create a new Google Sheet
    sheet_metadata = {
        'name': sheet_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }
    
    try:
        sheet = drive_service.files().create(body=sheet_metadata).execute()
        print("New sheet created:", sheet)
    
        # Get the ID of the newly created Google Sheet
        sheet_id = sheet['id']

        # Return the ID of the created Google Sheet
        return sheet_id
    except Exception as e:
        print("Error creating sheet:", e)
        return None

google_service_account_key = './aws-secops-17fe3efe6286.json'

# The ID of a folder in Google Drive that was shared with the service account, NOT a folder in a Google Shared Drive!
google_folder_id =  '1XIHyAGbU2UnzA4yksh9c1JogoZ3mzgCi'

today = datetime.date.today()
google_sheet_name = f"AWSSecurityGroups-Audit-{today.strftime('%b-%d-%Y')}"
create_google_sheet(google_service_account_key, google_folder_id, google_sheet_name)