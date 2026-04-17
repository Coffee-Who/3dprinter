# 請檢查程式碼中是否有這一段
import requests

# 確保 URL 是正確的
url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest" 

headers = {
    'X-Master-Key': JSONBIN_MASTER_KEY
}

# 執行請求
response = requests.get(url, headers=headers)
data = response.json()

# 注意：JSONBin v3 的資料結構是在 'record' 欄位下
if 'record' in data:import streamlit as st
import requests

# 1. 填入您的正確資訊
JSONBIN_MASTER_KEY = "$2a$10$NmH85djTPLNNMfQu4xJ.0uOLgN09L1GvrTK4dOP2B/rCzqfH6lo9."
JSONBIN_BIN_ID = "69e2028a36566621a8c2868e"

def get_jsonbin_data():
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    headers = {'X-Master-Key': JSONBIN_MASTER_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        # 如果回傳 200 表示成功
        if response.status_code == 200:
            return response.json().get('record')
        else:
            st.error(f"JSONBin 讀取失敗：狀態碼 {response.status_code}")
            st.write(response.json()) # 顯示錯誤細節
            return None
    except Exception as e:
        st.error(f"連線發生錯誤：{e}")
        return None

# 執行讀取
data = get_jsonbin_data()

if data:
    st.success("✅ 成功連線至 JSONBin！")
    # 這裡放原本顯示 3D 印表機資料的邏輯
    # final_data = data 
else:
    st.warning("目前無法取得雲端資料，請檢查 API Key 與 Bin ID。")
    final_data = data['record']
else:
    final_data = data # 預設回傳

