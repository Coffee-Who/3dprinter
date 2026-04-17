JSONBIN_MASTER_KEY = st.secrets["$2a$10$i8COKSrTKdtvxAwfLVDbte2AoL7Nar3oLKA7ZgQWZrfrLlEC8YluyY"]
JSONBIN_BIN_ID = st.secrets["69e2350daaba8821970cbb6c"]
# 確保請求標頭（Headers）包含 Master Key
headers = {
    'X-Master-Key': JSONBIN_MASTER_KEY,
    'Content-Type': 'application/json'

