import streamlit as st
import pandas as pd
from stl import mesh
import trimesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印報價", layout="wide")

# [登入邏輯與 CSS 保持不變，略過...]
# ... (請沿用前一版本的黑底白字登入與 CSS) ...

# 5. 主程式
if "password_correct" in st.session_state:
    # [選單邏輯略過...]
    
    st.title("💰 3D列印報價")
    input_method = st.radio("體積來源", ["📤 上傳 STL/STEP", "⌨️ 手動輸入"], horizontal=True)
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL/STEP":
        up_file = st.file_uploader("Upload", type=["stl", "step", "stp"], label_visibility="collapsed")
        
        if up_file:
            ext = os.path.splitext(up_file.name)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            try:
                if ext == ".stl":
                    your_mesh = mesh.Mesh.from_file(t_path)
                    vol_mm3 = int(abs(your_mesh.get_mass_properties()[0]))
                    vertices_raw = your_mesh.points.reshape(-1, 3)
                else:
                    # --- 💥 強化 STEP 讀取邏輯 ---
                    try:
                        # 使用 cascadio 作為後端（trimesh 推薦方式）
                        scene = trimesh.load(t_path)
                        # 將 Scene 合併為一個 Mesh
                        mesh_obj = scene.dump(concatenate=True) if isinstance(scene, trimesh.Scene) else scene
                        
                        # 核心計算：先試 filled_volume (處理微小破面)
                        vol_mm3 = int(abs(mesh_obj.filled_volume))
                        
                        if vol_mm3 <= 0:
                            vol_mm3 = int(abs(mesh_obj.volume))
                            
                        # 如果還是 0，嘗試凸包體積 (Convex Hull) 做最後掙扎
                        if vol_mm3 <= 0:
                            vol_mm3 = int(mesh_obj.convex_hull.volume)
                            
                        vertices_raw = mesh_obj.vertices[mesh_obj.faces].reshape(-1, 3)
                    except Exception as inner_e:
                        st.error(f"STEP 解析引擎錯誤: 請確認是否有安裝 cascadio 套件。詳細: {inner_e}")
                        vol_mm3 = 0

                # [3D 預覽與報價顯示邏輯保持不變...]
                if vol_mm3 > 0:
                    st.success(f"✅ 解析成功！偵測體積為: {vol_mm3:,} mm³")
                    # ... (後續報價與 UI 邏輯)
                else:
                    st.error("❌ 無法從該檔案獲取體積。請檢查模型是否為『實體(Solid)』而非曲面。")

            except Exception as e:
                st.error(f"檔案解析失敗: {e}")
            finally:
                if os.path.exists(t_path): os.remove(t_path)
