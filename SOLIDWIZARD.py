# =========================
# 5. 編輯面板 (修正版)
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    
    with st.expander("🛠️ 編輯項目資料", expanded=True):
        # 1. 編輯時的上傳器 (放在表單外，因為上傳會觸發即時 Rerun)
        new_file = st.file_uploader("更換圖片 (上傳後自動更新網址)", type=["jpg","png"], key="edit_upload")
        if new_file:
            with st.spinner("正在上傳新圖片..."):
                uploaded_url = upload_to_github(new_file)
                if uploaded_url:
                    item['img'] = uploaded_url
                    st.success("圖片已自動更新！")

        # 2. 開始表單
        with st.form("edit_form"):
            new_t = st.text_input("標題", value=item['title'])
            new_u = st.text_input("網址", value=item['url'])
            new_i = st.text_input("圖片網址 (手動微調)", value=item['img'])
            
            # 使用 columns 讓按鈕並排
            col_save, col_cancel = st.columns(2)
            
            # 關鍵修正：表單內必須使用 form_submit_button
            if col_save.form_submit_button("💾 儲存所有修改"):
                st.session_state.cards[info['cat']][info['idx']] = {"title": new_t, "img": new_i, "url": new_u}
                st.session_state.edit_info = None
                st.rerun()
                
            if col_cancel.form_submit_button("❌ 取消編輯"):
                st.session_state.edit_info = None
                st.rerun()
