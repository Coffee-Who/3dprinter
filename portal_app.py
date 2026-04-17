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
if 'record' in data:
    final_data = data['record']
else:
    final_data = data # 預設回傳

