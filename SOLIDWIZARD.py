import streamlit as st
import requests
import base64
import json
import time

# =========================
# CONFIG
# =========================
REPO = "Coffee-Who/3dprinter"
BRANCH = "main"
DATA_PATH = "data/portal.json"

TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(layout="wide", page_title="實威國際 Portal V2")

# =========================
# GITHUB - LOAD JSON
# =========================
def load_data():
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{DATA_PATH}?t={int(time.time())}"
    try:
        return requests.get(url).json()
    except:
        return {"categories": []}


# =========================
# GITHUB - SAVE JSON
# =========================
def save_data(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{DATA_PATH}"

    r = requests.get(url, headers={
        "Authorization": f"token {TOKEN}"
    })

    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")

    content = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=2).encode()
    ).decode()

    payload = {
        "message": "update portal data",
        "content": content,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, json=payload, headers={
        "Authorization": f"token {TOKEN}"
    })


# =========================
# IMAGE UPLOAD TO GITHUB
# =========================
def upload_image(file_bytes, filename):
    path = f"image/{filename}"
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"

    content = base64.b64encode(file_bytes).decode()

    payload = {
        "message": f"upload {filename}",
        "content": content,
        "branch": BRANCH
    }

    r = requests.put(url, json=payload, headers={
        "Authorization": f"token {TOKEN}"
    })

    if r.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"
    else:
        st.error(r.text)
        return None


# =========================
# LOAD SESSION DATA
# =========================
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# =========================
# UI HEADER
# =========================
st.title("🏢 實威國際入口網站 V2（企業雲端版）")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 重新同步"):
        st.session_state.data = load_data()
        st.rerun()

with col2:
    if st.button("💾 手動儲存"):
        save_data(data)
        st.success("已同步到 GitHub")


st.divider()


# =========================
# ADD CATEGORY
# =========================
st.subheader("➕ 新增分類")

cat_name = st.text_input("分類名稱")
cat_emoji = st.text_input("Emoji", "📁")

if st.button("新增分類"):
    if cat_name.strip() == "":
        st.warning("請輸入分類名稱")
    else:
        data["categories"].append({
            "id": f"cat_{int(time.time())}",
            "name": cat_name,
            "emoji": cat_emoji,
            "cards": []
        })
        save_data(data)
        st.rerun()


st.divider()


# =========================
# RENDER CATEGORIES
# =========================
for ci, cat in enumerate(data["categories"]):

    st.markdown(f"## {cat['emoji']} {cat['name']}")

    # -------------------------
    # CARDS
    # -------------------------
    cols = st.columns(4)

    for i, card in enumerate(cat["cards"]):
        with cols[i % 4]:
            if card.get("img"):
                st.image(card["img"], use_container_width=True)

            st.markdown(f"### {card['title']}")
            st.link_button("開啟", card["url"])

            if st.button("🗑 刪除", key=f"del_{ci}_{i}"):
                del data["categories"][ci]["cards"][i]
                save_data(data)
                st.rerun()


    # =========================
    # ADD CARD
    # =========================
    with st.expander("➕ 新增連結"):
        title = st.text_input("名稱", key=f"title_{ci}")
        url = st.text_input("網址", key=f"url_{ci}")
        img = st.file_uploader("圖片", type=["png", "jpg", "jpeg"], key=f"img_{ci}")

        if st.button("新增", key=f"add_{ci}"):

            if title.strip() == "" or url.strip() == "":
                st.warning("請填寫完整資料")
            else:

                img_url = ""

                if img:
                    filename = f"{int(time.time())}.jpg"
                    img_url = upload_image(img.read(), filename)

                data["categories"][ci]["cards"].append({
                    "title": title,
                    "url": url,
                    "img": img_url
                })

                save_data(data)
                st.rerun()


st.divider()
st.caption("V2 Enterprise Portal · GitHub Sync Edition")
