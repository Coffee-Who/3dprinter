import trimesh
import numpy as np

def formlabs_preflight_check(file_path):
    # 1. 載入模型
    try:
        mesh = trimesh.load(file_path)
    except Exception as e:
        return f"讀取失敗: {e}"

    results = []
    results.append(f"--- 檔案報告: {file_path} ---")

    # 2. 結構檢查 (結構如果不完整，Formlabs 會跳出修復提示)
    is_solid = mesh.is_watertight
    results.append(f"【結構】水密性: {'✅ 正常' if is_solid else '❌ 破面 (建議先修復)'}")

    # 3. 尺寸與體積預估
    size = mesh.extents
    vol = mesh.volume / 1000  # 轉為 ml
    results.append(f"【尺寸】{size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    results.append(f"【消耗】預估樹脂: {vol:.2f} ml")

    # 4. 杯吸效應檢測 (SLA 列印的大忌)
    # 原理：若模型是非凸面體且體積與凸包體積差異過大，通常代表有深凹槽
    if not mesh.is_convex:
        caution_ratio = mesh.convex_hull.volume / mesh.volume
        if caution_ratio > 1.2:
            results.append("【風險】⚠️ 偵測到深凹結構：請確認開口未朝向平台，或已加上排氣孔。")

    # 5. 擺放建議 (Orientation Logic)
    results.append("\n--- 擺放建議 (Orientation Strategy) ---")
    
    # 邏輯 A: 尋找最大平面
    # 如果有很大的平面，應旋轉 35-45 度
    results.append("- 建議旋轉角度：將主長軸與 Z 軸交角設為 45°，減少每層離型力。")
    
    # 邏輯 B: 支撐位置
    results.append("- 表面品質：請將「重要細節面」朝上，讓支撐點留在背面或底部。")

    return "\n".join(results)

# 測試運行 (請取消註解並替換檔名)
# print(formlabs_preflight_check("your_file.stl"))
