import requests
import re
import json
import os

UID = "7765938906"
WEBHOOK = os.getenv("WEBHOOK")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://m.weibo.cn/",
    "Accept": "application/json, text/plain, */*"
}

STATE_FILE = "last.json"

# 🧹 Xóa HTML
def clean_html(raw):
    return re.sub('<.*?>', '', raw or "")

# 🌐 Dịch sang tiếng Việt
def translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "vi",
            "dt": "t",
            "q": text
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        return "".join([i[0] for i in data[0]])
    except Exception as e:
        print("Lỗi dịch:", e)
        return text

# 📩 Gửi Discord
def send_embed(text, vi_text, url, image=None):
    if not WEBHOOK:
        print("❌ Thiếu WEBHOOK")
        return

    desc = f"🇨🇳 {text[:1000]}\n\n🇻🇳 {vi_text[:1000]}"

    data = {
        "content": "📢 Có bài mới!",
        "embeds": [
            {
                "title": "Weibo mới",
                "description": desc,
                "url": url,
                "color": 16711680
            }
        ]
    }

    if image and isinstance(image, str) and image.startswith("http"):
        data["embeds"][0]["image"] = {"url": image}

    try:
        res = requests.post(WEBHOOK, json=data, timeout=10)
        print("Discord status:", res.status_code)
        print("Response:", res.text)
    except Exception as e:
        print("Lỗi gửi Discord:", e)

# 📥 Lấy bài mới nhất
def get_latest():
    try:
        url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={UID}&containerid=107603{UID}"

        res = requests.get(url, headers=HEADERS, timeout=10)
        print("Status:", res.status_code)

        if res.status_code != 200:
            print("Request lỗi:", res.text[:200])
            return None

        data = res.json()
        cards = data.get("data", {}).get("cards", [])

        for c in cards:
            if c.get("mblog"):
                m = c["mblog"]
                return {
                    "id": m.get("id"),
                    "text": clean_html(m.get("text")),
                    "image": m.get("pics", [{}])[0].get("large", {}).get("url"),
                    "url": f"https://weibo.com/{UID}/{m.get('id')}"
                }

    except Exception as e:
        print("Lỗi API Weibo:", e)

    return None

# 💾 Load bài cũ
def load_last():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

# 💾 Lưu bài mới
def save_last(data):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Lỗi lưu file:", e)

# 🚀 MAIN
def main():
    last = load_last()

    # TEST WEBHOOK

    post = get_latest()

    if not post:
        print("⚠️ Không lấy được dữ liệu Weibo")
        return

    print("POST:", post)

    post_id = post.get("id")
    text = post.get("text", "")
    image = post.get("image")
    url = post.get("url")

    if not post_id:
        print("⚠️ Post không hợp lệ")
        return

    # Force gửi để test
    if post_id != last.get("id"):
        print("✅ Gửi Discord")
        vi_text = translate(text)
        send_embed(text, vi_text, url, image)
        save_last(post)
    else:
        print("⏳ Không có bài mới")

if __name__ == "__main__":
    main()
