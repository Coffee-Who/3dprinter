import streamlit as st
import trimesh
import numpy as np
import io
from stl_viewer import stl_viewer # 導入 3D 預覽組件

# 1. 網頁基本設定
st.set_page_config(page_title="Formlabs 支撐模擬器", layout="wide")
st.title("🖨️ 3D 列印「支撐架」生成與擺放模擬")

# --- 側邊欄設定 ---
st.sidebar.header("支撐參數設定")
support_density = st.sidebar.slider("支撐密度 (點/cm²)", 1.0, 5.0, 2.0, 0.5)
touchpoint_size = st.sidebar.slider("接觸點直徑 (mm)", 0.3, 1.0, 0.6, 0.1)
raft_thickness = st.sidebar.slider("底座厚度 (mm)", 1.0, 5.0, 2.0, 0.5)

# --- 核心邏輯：生成簡易支撐架 ---
def generate_simple_supports(mesh, density, touch_size, raft_thick):
    """
    簡易支撐生成演算法：
    1. 找出懸空面 (法向量向下)
    2. 在這些面上採樣生成支撐點
    3. 向上生成圓柱體，並加入基座
    """
    # 获取模型的邊界盒
    bounds = mesh.bounds
    min_z = bounds[0][2]
    
    # a. 尋找懸空面 (Overhangs)
    # 篩選出法向量 Z 分量小於 -0.7 的面 (約 45度角)
    overhang_faces_indices = np.where(mesh.face_normals[:, 2] < -0.7)[0]
    if len(overhang_faces_indices) == 0:
        return None, None
    
    overhang_mesh = mesh.submesh([overhang_faces_indices], append=True)
    
    # b. 在懸空面上採樣生成點 (按密度)
    num_points = int(overhang_mesh.area * (density / 100)) # density is per cm2
    if num_points < 10: num_points = 10
    points, face_indices = overhang_mesh.sample(num_points, return_index=True)
    
    # c. 生成支撐柱 (Cylinders)
    support_structure = []
    
    # 基座平面
    raft_z = min_z - raft_thick - 5 # 讓模型與基座有 5mm 距離
    
    for p in points:
        # 生成圓柱體：從基座到採樣點
        height = p[2] - raft_z
        if height > 0:
            cylinder = trimesh.creation.cylinder(radius=touch_size/2, height=height)
            # 將圓柱體移到正確位置 (預設是中心在原點)
            translation = [p[0], p[1], raft_z + height/2]
            cylinder.apply_translation(translation)
            support_structure.append(cylinder)

    # d. 生成基座 (Raft)
    if support_structure:
        all_supports = trimesh.util.concatenate(support_structure)
        
        # 簡易矩形底座
        extents = mesh.extents
        raft = trimesh.creation.box(extents=[extents[0]*1.2, extents[1]*1.2, raft_thick])
        raft.apply_translation([mesh.center_mass[0], mesh.center_mass[1], raft_z - raft_thick/2])
        
        return all_supports, raft
    
    return None, None

# --- 網頁主流程 ---
uploaded_file = st.file_uploader("上傳 STL 模型 (建議檔案小於 10MB)", type=["stl"])

if uploaded_file is not None:
    try:
        # 1. 載入模型
        file_bytes = uploaded_file.read()
        mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        
        # 2. 自動優化擺放：旋轉 45 度
        st.info("💡 系統已自動將模型旋轉 45 度，以優化 SLA 列印成功率。")
        rotation = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh.apply_transform(rotation)
        
        # 3. 顯示分析
        with st.expander("📊 模型分析與風險"):
            col1, col2 = st.columns(2)
            col1.write(f"模型尺寸: {np.round(mesh.extents, 1)} mm")
            col2.write(f"預估樹脂量: {mesh.volume/1000:.2f} ml")
            if not mesh.is_watertight:
                st.warning("❌ 模型有破面，可能影響支撐生成，請在 PreForm 修復。")

        # 4. 生成支撐與合併模型
        with st.spinner("正在生成虛擬支撐架... (這可能需要幾秒鐘)"):
            supports, raft = generate_simple_supports(mesh, support_density, touchpoint_size, raft_thickness)
            
            if supports is not None:
                # 將模型、支撐、基座合併成一個新物件
                scene_meshes = [mesh, supports, raft]
                combined_mesh = trimesh.util.concatenate(scene_meshes)
                
                # 將合併後的模型存為 BytesIO 供預覽器使用
                stl_io = io.BytesIO()
                combined_mesh.export(stl_io, file_type='stl')
                stl_io.seek(0)
                
                # 5. 顯示 3D 互動預覽 (使用 streamlit-stl)
                st.subheader("📦 3D 模擬預覽 (包含支撐架與基座)")
                st.write("使用滑鼠旋轉、縮放，確認支撐位置。")
                
                # 使用 stl_viewer 顯示合併後的模型
                stl_viewer(stl_io)
                
                st.success("✅ 簡易支撐模擬完成！實際列印前請以 PreForm 的計算為準。")
            else:
                st.error("無法生成支撐，可能是模型結構過於簡單或非水密。")
                stl_viewer(uploaded_file) # 顯示原始模型

    except Exception as e:
        st.error(f"處理檔案時發生錯誤: {e}")

else:
    st.info("請上傳一個 .stl 檔案以開始模擬。")
