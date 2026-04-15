# =====================
# EDIT PANEL（完整修正版）
# =====================
if st.session_state.edit:
    cat, idx = st.session_state.edit
    item = st.session_state.cards[cat][idx]

    st.markdown("## ✏️ 編輯項目")

    # ✔ 可編輯：名稱 / 圖片 / 連結
    new_title = st.text_input("名稱", value=item["title"])
    new_img = st.text_input("圖片連結", value=item["img"])
    new_url = st.text_input("網站連結", value=item["url"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("儲存修改"):
            st.session_state.cards[cat][idx] = {
                "title": new_title,
                "img": new_img,
                "url": new_url
            }
            st.session_state.edit = None
            st.rerun()

    with col2:
        if st.button("取消"):
            st.session_state.edit = None
            st.rerun()
