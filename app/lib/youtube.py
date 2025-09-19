import os, re, requests

API_KEY = os.getenv("YOUTUBE_API_KEY")

def parse_video_id(url:str)->str:
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", url)
    return m.group(1) if m else ""

def fetch_meta(url:str):
    vid = parse_video_id(url)
    title=desc=thumb=None

    # 1) official API
    if API_KEY and vid:
        r = requests.get(
          "https://www.googleapis.com/youtube/v3/videos",
          params={"part":"snippet","id":vid,"key":API_KEY}, timeout=10)
        if r.ok and r.json().get("items"):
            sn = r.json()["items"][0]["snippet"]
            title = sn.get("title"); desc = sn.get("description")
            thumbs = sn.get("thumbnails",{})
            pick = thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or {}
            thumb = pick.get("url")

    # 2) fallback: oEmbed
    if not title:
        r = requests.get("https://www.youtube.com/oembed",
                         params={"url":url,"format":"json"}, timeout=10)
        if r.ok:
            j = r.json()
            title = j.get("title")
            thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg" if vid else None

    # 3) last resort: thumbnail url only
    if not thumb and vid:
        thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"

    return {"video_id":vid, "title":title or "タイトル不明", "description":desc or "", "thumbnail_url":thumb}
