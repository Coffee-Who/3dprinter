"""
JSONBin.io 設定測試腳本
執行方式：python jsonbin_setup.py
"""
import requests
import json

# ★ 把你的 Master Key 貼在這裡 ★
MASTER_KEY = "$2a$10$0oZ3tRXXuInYI61c38vJbuBpQwxtuaXxsKjliUwMm39b2kZDtfD/S"   # 例如：$2a$10$abcdefg...

# ════════════════════════════════
print("=" * 60)
print("  JSONBin.io 連線測試")
print("=" * 60)

if not MASTER_KEY:
    print()
    print("❌ 尚未填入 Master Key！")
    print()
    print("請依照以下步驟：")
    print("  1. 用瀏覽器開啟：https://jsonbin.io")
    print("  2. 點右上角 Sign Up 免費註冊")
    print("  3. 登入後點右上角頭像 → API Keys")
    print("  4. 複製 SECRET KEY（以 $2a$ 開頭）")
    print("  5. 貼到本腳本第 8 行 MASTER_KEY = \"\" 的引號裡")
    print("  6. 存檔後重新執行：python jsonbin_setup.py")
    print()
    input("按 Enter 結束...")
    exit()

print(f"\n✅ Master Key 已填入（前10碼）：{MASTER_KEY[:10]}...")
print("\n正在連線至 JSONBin.io ...\n")

# ════════════════════════════════
# 建立初始資料
initial_data = {
    "categories": [
        {
            "id": "internal", "name": "A · 內部系統", "emoji": "🏢",
            "cards": [
                {"title": "CRM",      "url": "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx", "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=640&q=80"},
                {"title": "EIP",      "url": "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx",           "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=640&q=80"},
                {"title": "EASYFLOW", "url": "http://192.168.100.85/efnet/",                                            "img": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640&q=80"},
                {"title": "請假系統", "url": "http://192.168.2.251/MotorWeb/CHIPage/Login.asp",                        "img": "https://images.unsplash.com/photo-1508385082359-f38ae991e8f2?w=640&q=80"},
            ]
        },
        {
            "id": "official", "name": "B · 官方系統", "emoji": "🌐",
            "cards": [
                {"title": "實威國際官網",     "url": "https://www.swtc.com/zh-tw/",          "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640&q=80"},
                {"title": "實威國際 YouTube", "url": "https://www.youtube.com/@solidwizard", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=640&q=80"},
                {"title": "智慧製造 YouTube", "url": "https://www.youtube.com/@SWTCIM",      "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=640&q=80"},
                {"title": "實威知識+",        "url": "https://www.youtube.com/@實威知識",    "img": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=640&q=80"},
            ]
        },
        {
            "id": "solidworks", "name": "C · SOLIDWORKS", "emoji": "⚙️",
            "cards": [
                {"title": "SOLIDWORKS 官網",  "url": "https://www.solidworks.com/",   "img": "https://cdn.jsdelivr.net/gh/Coffee-Who/3dprinter@main/image/SOLIDWORKS.jpg"},
                {"title": "MySolidWorks",     "url": "https://my.solidworks.com/",    "img": "https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=640&q=80"},
                {"title": "SOLIDWORKS Forum", "url": "https://forum.solidworks.com/", "img": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=640&q=80"},
            ]
        },
        {
            "id": "formlabs", "name": "C · Formlabs", "emoji": "🖨️",
            "cards": [
                {"title": "Formlabs 原廠",      "url": "https://formlabs.com/",            "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e?w=640&q=80"},
                {"title": "Formlabs Support",   "url": "https://support.formlabs.com/",   "img": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=640&q=80"},
                {"title": "Formlabs Dashboard", "url": "https://dashboard.formlabs.com/", "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=640&q=80"},
            ]
        },
        {
            "id": "scanology", "name": "D · SCANOLOGY", "emoji": "📡",
            "cards": [
                {"title": "SCANOLOGY 官網", "url": "https://www.scanology.com/", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=640&q=80"},
            ]
        },
    ]
}

try:
    resp = requests.post(
        "https://api.jsonbin.io/v3/b",
        headers={
            "Content-Type":  "application/json",
            "X-Master-Key":  MASTER_KEY,
            "X-Bin-Name":    "swtc-portal",
            "X-Bin-Private": "false",
        },
        json=initial_data,
        timeout=15
    )

    if resp.status_code == 200 or resp.status_code == 201:
        result = resp.json()
        bin_id = result["metadata"]["id"]

        print("🎉 成功建立 JSONBin！")
        print()
        print("=" * 60)
        print("  請把以下兩行複製到 portal_app.py 的設定區：")
        print("=" * 60)
        print()
        print(f'  JSONBIN_MASTER_KEY = "{MASTER_KEY}"')
        print(f'  JSONBIN_BIN_ID     = "{bin_id}"')
        print()
        print("=" * 60)
        print()
        print("步驟：")
        print("  1. 用記事本開啟 portal_app.py")
        print("  2. 找到設定區（第 15~17 行）")
        print("  3. 把上方兩行貼進去取代原本的內容")
        print("  4. 存檔")
        print("  5. 重新執行：streamlit run portal_app.py")
        print()

        # 存到本機方便複製
        config = {
            "JSONBIN_MASTER_KEY": MASTER_KEY,
            "JSONBIN_BIN_ID": bin_id
        }
        with open("jsonbin_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ 設定也已自動儲存到 jsonbin_config.json")

    elif resp.status_code == 401:
        print("❌ Master Key 錯誤（401 Unauthorized）")
        print()
        print("請確認：")
        print("  · Key 是否完整複製（通常很長，以 $2a$10$ 開頭）")
        print("  · 登入 jsonbin.io → API Keys 頁面重新複製")

    elif resp.status_code == 429:
        print("❌ 請求次數超限（429 Too Many Requests）")
        print("請稍等 1 分鐘後再試")

    else:
        print(f"❌ 建立失敗，狀態碼：{resp.status_code}")
        print(f"回應內容：{resp.text}")

except requests.exceptions.ConnectionError:
    print("❌ 無法連線到 JSONBin.io")
    print("請確認電腦有連接網路")

except requests.exceptions.Timeout:
    print("❌ 連線逾時，請稍後再試")

except Exception as e:
    print(f"❌ 發生錯誤：{e}")

print()
input("按 Enter 結束...")
