from flask import Flask, request, jsonify, render_template, send_file
import csv, os, subprocess
from datetime import datetime

app = Flask(__name__, template_folder="templates")

DATA_DIR = "data"
LINKS_CSV = os.path.join(DATA_DIR, "links_store.csv")
MASTER_CSV = os.path.join(DATA_DIR, "master_uploads.csv")
LOG_FILE = os.path.join("logs", "engine.log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("temp/downloads", exist_ok=True)

def ensure_csv(path, headers):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)

ensure_csv(LINKS_CSV, ["reel_url", "status", "added_at"])
ensure_csv(MASTER_CSV, ["reel_url", "caption", "youtube_id", "uploaded_at"])

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add-links", methods=["POST"])
def add_links():
    links = request.json.get("links", [])
    existing = {r["reel_url"] for r in read_csv(LINKS_CSV)} | \
               {r["reel_url"] for r in read_csv(MASTER_CSV)}

    added = 0
    with open(LINKS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for link in links:
            if link and link not in existing:
                writer.writerow([link, "pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                added += 1

    return jsonify({"added": added})

@app.route("/start", methods=["POST"])
def start_engine():
    subprocess.Popen(["python", "engine.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jsonify({"status": "started"})

@app.route("/stats")
def stats():
    links = read_csv(LINKS_CSV)
    uploads = read_csv(MASTER_CSV)

    pending = sum(1 for r in links if r.get("status") == "pending")

    today = datetime.now().strftime("%Y-%m-%d")
    today_uploads = sum(
        1 for r in uploads
        if r.get("uploaded_at", "").startswith(today)
    )

    last_upload = None
    for r in reversed(uploads):
        if r.get("uploaded_at"):
            last_upload = r["uploaded_at"]
            break

    return jsonify({
        "pending_links": pending,
        "today_uploads": today_uploads,
        "last_upload_time": last_upload
    })

@app.route("/logs")
def logs():
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/csv")
def csv_download():
    return send_file(MASTER_CSV, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
