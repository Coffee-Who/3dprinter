@st.cache_data(ttl=600)
def get_images():
    try:
        url = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image?ref=main"
        response = requests.get(url)

        if response.status_code != 200:
            st.error("GitHub 連線失敗")
            st.write(response.text)
            return []

        data = response.json()

        images = []
        for file in data:
            if file["name"].lower().endswith(("png", "jpg", "jpeg")):
                images.append({
                    "name": file["name"],
                    "url": file["download_url"]
                })

        return images

    except Exception as e:
        st.error(f"錯誤：{e}")
        return []
