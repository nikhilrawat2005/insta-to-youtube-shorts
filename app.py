import os, json, random, csv, time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

app = Flask(__name__)

STORE_FOLDER = "store"
CSV_FILE = "upload_log.csv"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

os.makedirs(STORE_FOLDER, exist_ok=True)

# ---------- CSV INIT ----------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_name", "store", "upload", "caption", "date", "time"])

# ---------- CSV HELPERS ----------
def read_csv():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(rows):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["video_name", "store", "upload", "caption", "date", "time"]
        )
        writer.writeheader()
        writer.writerows(rows)

# ---------- UTILS ----------
def get_next_video_number():
    rows = read_csv()
    last = 0
    for r in rows:
        try:
            n = int(r["video_name"].replace("video_", "").replace(".mp4", ""))
            last = max(last, n)
        except:
            pass
    return last + 1

def get_random_caption():
    with open("captions.json", "r", encoding="utf-8") as f:
        captions = json.load(f).get("captions", [])
    return random.choice(captions) if captions else "ai #shorts #viral"

def get_youtube():
    if not os.path.exists("token.json"):
        raise RuntimeError("token.json not found")

    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )
    return build("youtube", "v3", credentials=creds)

# ---------- ROUTES ----------
@app.route("/")
def dashboard():
    rows = read_csv()

    store_count = sum(1 for r in rows if r["store"] == "downloaded")
    upload_count = sum(1 for r in rows if r["upload"] == "yes")

    last_upload = None
    for r in rows:
        if r["upload"] == "yes":
            last_upload = f"{r['date']} {r['time']}"

    return render_template(
        "dashboard.html",
        logs=rows[::-1],
        store_count=store_count,
        upload_count=upload_count,
        last_upload=last_upload
    )

@app.route("/store", methods=["POST"])
def store_video():
    rows = read_csv()
    files = request.files.getlist("video")

    base = get_next_video_number()

    for i, file in enumerate(files):
        name = f"video_{base + i}.mp4"
        file.save(os.path.join(STORE_FOLDER, name))

        rows.append({
            "video_name": name,
            "store": "downloaded",
            "upload": "no",
            "caption": "",
            "date": "",
            "time": ""
        })

    write_csv(rows)
    return redirect(url_for("dashboard"))

@app.route("/upload", methods=["POST"])
def upload_video():
    files = os.listdir(STORE_FOLDER)
    if not files:
        return redirect(url_for("dashboard"))

    video = files[0]
    path = os.path.join(STORE_FOLDER, video)
    caption = get_random_caption()

    yt = get_youtube()
    yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": caption,  # ✅ JSON CAPTION ONLY
                "description": caption,   # ✅ JSON CAPTION ONLY
                "tags": caption.split(),
                "categoryId": "22"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(path, resumable=True)
    ).execute()

    time.sleep(1)
    os.remove(path)

    rows = read_csv()
    now = datetime.now()

    for r in rows:
        if r["video_name"] == video:
            r["store"] = "delete"
            r["upload"] = "yes"
            r["caption"] = caption
            r["date"] = now.strftime("%Y-%m-%d")
            r["time"] = now.strftime("%H:%M:%S")
            break

    write_csv(rows)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
