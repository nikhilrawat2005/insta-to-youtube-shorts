import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET = "client_secret.json"
TOKEN_FILE = "secrets/token.json"

def get_youtube():
    if not os.path.exists(CLIENT_SECRET):
        raise RuntimeError("YouTube credentials missing")

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
        creds = flow.run_local_server(port=0)
        os.makedirs("secrets", exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_short(video_path, caption):
    youtube = get_youtube()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": caption[:90],
                "description": caption,
                "categoryId": "22"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    )
    response = request.execute()
    return response["id"]
