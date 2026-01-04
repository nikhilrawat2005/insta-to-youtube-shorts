import os, csv, subprocess, random
from datetime import datetime
from caption_manager import get_caption
from uploader import upload_short

LINKS_CSV = "data/links_store.csv"
MASTER_CSV = "data/master_uploads.csv"
LOG_FILE = "logs/engine.log"
TEMP_DIR = "temp/downloads"

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def pop_next_link():
    rows = []
    chosen = None

    with open(LINKS_CSV, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    for r in reader:
        if r["status"] == "pending" and not chosen:
            chosen = r
        else:
            rows.append(r)

    if chosen:
        with open(LINKS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=reader[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    return chosen["reel_url"] if chosen else None

def download_reel(url):
    os.makedirs(TEMP_DIR, exist_ok=True)
    out = os.path.join(TEMP_DIR, "video.mp4")
    subprocess.run(["yt-dlp", "-f", "mp4", "-o", out, url], check=True)
    return out

def save_master(url, caption, yt_id):
    with open(MASTER_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([url, caption, yt_id, datetime.now().isoformat()])

def run_engine():
    log("🟢 Engine started")

    url = pop_next_link()
    if not url:
        log("❌ No pending links")
        return

    caption = get_caption()
    log(f"🎯 Reel: {url}")
    log(f"📝 Caption: {caption}")

    video = download_reel(url)
    log("⬇️ Downloaded")

    yt_id = upload_short(video, caption)
    log(f"📤 Uploaded → {yt_id}")

    save_master(url, caption, yt_id)
    os.remove(video)

    log("🗑️ Temp deleted")
    log("🏁 Engine finished")

if __name__ == "__main__":
    run_engine()
