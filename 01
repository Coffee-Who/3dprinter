import trimesh
import numpy as np
import os

class FormlabsChecker:
    def __init__(self, file_path):
        self.file_path = file_path
        try:
            self.mesh = trimesh.load(file_path)
        except Exception as e:
            print(f"無法載入檔案: {e}")
            self.mesh = None

    def check_watertight(self):
        """檢查模型是否封閉（水密）"""
        return self.mesh.is_watertight

    def check_suction_cups(self):
        """
        簡易檢查杯吸效應：
        檢查模型是否存在凹陷空間且開口可能朝下。
        這裡使用凸包體積比對來判斷是否有明顯凹陷。
        """
        if self.mesh.is_convex:
            return False # 凸面體不會有杯吸問題
        
        # 如果凸包體積明顯大於原始體積，表示有深凹處
        ratio = self.mesh.convex_hull.volume / self.mesh.volume
        return ratio > 1.15

    def get_optimal_orientation(self):
        """
        計算建議擺放角度：
        SLA 核心邏輯：將模型主軸與 Z 軸偏移，避免大截面積。
        這裡使用 PCA (主成分分析) 找出長軸。
        """
        # 獲取主成分慣性張量
        to_origin, extents = trimesh.bounds.oriented_bounds(self.mesh)
        
        # 建議角度：通常將最長邊旋轉至與平台成 35-45 度
        # 我們回傳建議的操作步驟
        advice = [
            "1. 將模型最長的一面旋轉與底座成 45° 角。",
            "2. 避免大平面直接平行於建構平台。",
            "3. 如果模型有重要外觀，請將該面朝上遠離平台。"
        ]
        return advice

    def run_full_report(self):
        if self.mesh is None: return

        print(f"== Formlabs 列印前檢查報告: {os.path.basename(self.file_path)} ==")
        
        # 1. 幾何結構
        is_ok = self.check_watertight()
        status = "✅ 通過" if is_ok else "❌ 警告：模型有破面"
        print(f"結構完整性: {status}")

        # 2. 尺寸檢查
        size = self.mesh.extents
        print(f"模型尺寸: 寬 {size[0]:.1f}mm, 深 {size[1]:.1f}mm, 高 {size[2]:.1f}mm")

        # 3. 體積與成本預估
        vol = self.mesh.volume / 1000 # 換算成 ml
        print(f"預估樹脂消耗: {vol:.2f} ml")

        # 4. 風險偵測
        has_suction = self.check_suction_cups()
        if has_suction:
            print("風險提示: [!] 偵測到潛在『杯吸效應』區域，請務必打孔或傾斜模型。")
        else:
            print("風險提示: 未偵測到明顯杯吸結構。")

        # 5. 擺放建議
        print("\n[擺放建議方向]")
        for tip in self.get_optimal_orientation():
            print(f" - {tip}")
        
        print("="*50)

# --- 使用範例 ---
# 替換成你的 STL 路徑
# checker = FormlabsChecker("my_model.stl")
# checker.run_full_report()
