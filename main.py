import requestsimport reimport jsonimport os
UID = "7765938906"WEBHOOK = os.getenv("WEBHOOK")
HEADERS = {    "User-Agent": "Mozilla/5.0"}
STATE_FILE = "last.json"

# Xóa HTMLdef clean_html(raw):    return re.sub('<.*?>', '', raw or "")

# Dịch sang tiếng Việtdef translate(text):    try:        url = "https://translate.googleapis.com/translate_a/single"        params = {            "client": "gtx",            "sl": "auto",            "tl": "vi",            "dt": "t",            "q": text        }        res = requests.get(url, params=params, timeout=10).json()        return "".join([i[0] for i in res[0]])    except Exception as e:        print("Lỗi dịch:", e)        return text

# Gửi Discorddef send_embed(text, vi_text, url, image=None):    if not WEBHOOK:        print(" Thiếu WEBHOOK")        return
    data = {        "embeds": [            {                "title": " Weibo mới",                "description": f" {text[:1000]}\n\n {vi_text[:1000]}",                "url": url,                "color": 16711680            }        ]    }
    if image:        data["embeds"][0]["image"] = {"url": image}
    try:        requests.post(WEBHOOK, json=data, timeout=10)    except Exception as e:        print("Lỗi gửi Discord:", e)

# Lấy bài mới nhấtdef get_latest():    try:        url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={UID}&containerid=107603{UID}"        res = requests.get(url, headers=HEADERS, timeout=10).json()
        cards = res.get("data", {}).get("cards", [])        for c in cards:            if c.get("mblog"):                m = c["mblog"]                return {                    "id": m.get("id"),                    "text": clean_html(m.get("text")),                    "image": m.get("pics", [{}])[0].get("large", {}).get("url"),                    "url": f"https://weibo.com/{UID}/{m.get('id')}"                }    except Exception as e:        print("Lỗi API Weibo:", e)
    return None

# Load bài cũdef load_last():    try:        if os.path.exists(STATE_FILE):            with open(STATE_FILE, "r") as f:                return json.load(f)    except:        pass    return {}

# Lưu bài mớidef save_last(data):    try:        with open(STATE_FILE, "w") as f:            json.dump(data, f)    except Exception as e:        print("Lỗi lưu file:", e)

# MAINdef main():    last = load_last()    post = get_latest()
    if not post:        print(" Không lấy được dữ liệu Weibo")        return
    post_id = post.get("id")    text = post.get("text", "")    image = post.get("image")    url = post.get("url")
    if not post_id:        print(" Post không hợp lệ")        return
    if post_id != last.get("id"):        print(" Có bài mới → gửi Discord")
        vi_text = translate(text)        send_embed(text, vi_text, url, image)
        save_last(post)    else:        print(" Không có bài mới")

if __name__ == "__main__":    main()
