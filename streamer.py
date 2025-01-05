import pathway as pw
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import os
import io

# Google Drive Setup
SERVICE_ACCOUNT_FILE = "credentials.json"  # Path to your service account JSON file
FOLDER_ID = "13eDgt0YghQU2qlogGrTrXJzfD0h0F2Iw"  # Google Drive folder ID
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Authenticate Google Drive API
def authenticate_google_drive():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)

# Download files from Google Drive
def download_files_from_drive(service, folder_id, destination):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    os.makedirs(destination, exist_ok=True)

    for file in files:
        file_id, file_name = file["id"], file["name"]
        file_path = os.path.join(destination, file_name)

        request = service.files().get_media(fileId=file_id)
        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloaded {file_name}: {int(status.progress() * 100)}%")

    return destination

# Load files into Pathway Table
def load_files_into_pathway(destination):
    rows = []
    for file_name in os.listdir(destination):
        with open(os.path.join(destination, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            rows.append({"file_name": file_name, "file_content": content})

    return pw.Table.from_records(rows)
# Main Workflow
if __name__ == "__main__":
    drive_service = authenticate_google_drive()
    download_path = "./downloaded_files"
    downloaded_folder = download_files_from_drive(drive_service, FOLDER_ID, download_path)
 
    # Create Pathway Table from downloaded files
    file_table = load_files_into_pathway(downloaded_folder)

    # Preview table content
    pw.io.print_table(file_table)
