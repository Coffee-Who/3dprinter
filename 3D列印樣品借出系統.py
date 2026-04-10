def get_images():
    try:
        response = requests.get(GITHUB_API)

        if response.status_code != 200:
            st.error(f"GitHub API 錯誤：{response.status_code}")
            return []

        data = response.json()

        # 🔥 防呆：確保是 list
        if not isinstance(data, list):
            st.error(f"GitHub 回傳格式錯誤：{data}")
            return []

        images = []
        for file in data:
            # 🔥 防呆：確保 key 存在
            if isinstance(file, dict) and "name" in file and "download_url" in file:
                if file["name"].lower().endswith(("png", "jpg", "jpeg")):
                    images.append({
                        "name": file["name"],
                        "url": file["download_url"]
                    })

        return images

    except Exception as e:
        st.error(f"讀取 GitHub 失敗：{e}")
        return []
