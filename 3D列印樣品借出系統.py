@st.cache_data(ttl=600)
def get_images():
    try:
        headers = {}  # 如果 private repo 就加 token

        response = requests.get(GITHUB_API, headers=headers)

        if response.status_code != 200:
            st.error(f"GitHub API 錯誤：{response.status_code}")
            st.write(response.text)
            return []

        data = response.json()

        # Debug用（確認資料）
        st.write("GitHub回傳：", data)

        if not isinstance(data, list):
            st.error("回傳不是圖片列表")
            return []

        images = []
        for file in data:
            if isinstance(file, dict):
                name = file.get("name", "")
                url = file.get("download_url", "")

                if name.lower().endswith(("png", "jpg", "jpeg")):
                    images.append({
                        "name": name,
                        "url": url
                    })

        if len(images) == 0:
            st.warning("⚠️ 有抓到資料，但沒有圖片")

        return images

    except Exception as e:
        st.error(f"錯誤：{e}")
        return []
