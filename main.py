import requests
import re
import json
import os

UID = "7765938906"
WEBHOOK = os.getenv("WEBHOOK")

HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_html(raw):
    return re.sub('<.*?>', '', raw)

def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client":"gtx","sl":"auto","tl":"vi","dt":"t","q":text}
        res = requests.get(url, params=params).json()
        return "".join([i[0] for i in res[0]])
    except:
        return text

def send_embed(text, vi_text, url, image=None):
    data = {
        "embeds":[{
            "title":"📢 Weibo mới",
            "description":f"🇨🇳 {text[:1000]}\n\n🇻🇳 {vi_text[:1000]}",
            "url":url,
            "color":16711680,
            "image":{"url":image} if image else {}
        }]
    }
    requests.post(WEBHOOK, json=data)

def get_latest():
    url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={UID}&containerid=107603{UID}"
    res = requests.get(url, headers=HEADERS).json()
    cards = res.get("data", {}).get("cards", [])
    for c in cards:
        if c.get("mblog"):
            m=c["mblog"]
            return {
                "id":m["id"],
                "text":clean_html(m["text"]),
                "image":m.get("pics",[{}])[0].get("large",{}).get("url"),
                "url":f"https://weibo.com/{UID}/{m['id']}"
            }

state_file="last.json"

def load_last():
    try:
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_last(data):
    json.dump(data, open(state_file,"w"))

last=load_last()
post = get_latest()
if not post:
    print("Không có dữ liệu")
    exit()

if post and post["id"]!=last.get("id"):
    vi=translate(post["text"])
    send_embed(post["text"],vi,post["url"],post["image"])
    save_last(post)
