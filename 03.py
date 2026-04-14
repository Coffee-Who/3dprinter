import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
import hashlib
import json
from scipy.spatial import cKDTree

# --- 1. PreForm 專業 UI 配置 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff;
        border: 1px solid #cbd5e1; height: 38px; font-size: 13px; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .price-result { color: #1e293b; font-size: 32px; font-weight: 800;
        border-bottom: 2px solid #0081FF; display: inline-block; margin-bottom: 10px; }
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .data-item { border-left: 3px solid #cbd5e1; padding-left: 10px; }
    .data-label { color: #64748b; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a; font-size: 14px; font-weight: 700; }
    .cost-breakdown { background: #f8fafc; border-radius: 6px; padding: 12px 16px;
        margin-top: 12px; border: 1px solid #e2e8f0; }
    .cost-row { display: flex; justify-content: space-between; font-size: 12px; color: #475569; padding: 3px 0; }
    .cost-row.total { font-weight: 700; color: #0f172a; border-top: 1px solid #cbd5e1;
        margin-top: 6px; padding-top: 6px; font-size: 13px; }
    .priority-note { background: #eff6ff; color: #1d4ed8; border-left: 3px solid #3b82f6;
        padding: 8px 12px; font-size: 12px; border-radius: 0 4px 4px 0; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心狀態初始化 ---
for k, v in [('offset',[0.0,0.0]),('mesh',None),('mesh_hash',""),('thin_faces',None)]:
    if k not in st.session_state: st.session_state[k] = v

# --- 3. 材料與設備規格 ---
@st.cache_data
def load_materials():
    data = {
        "材料名稱": [
            "Clear Resin V4","Grey Resin V4","White Resin V4","Black Resin V4",
            "Draft Resin V2","Model Resin V3","Tough 2000 Resin","Tough 1500 Resin",
            "Durable Resin","Grey Pro Resin","Rigid 10K Resin","Rigid 4000 Resin",
            "Flexible 80A Resin","Elastic 50A Resin","High Temp Resin","Flame Retardant Resin",
            "ESD Resin","BioMed Clear Resin","BioMed Amber Resin","BioMed White Resin",
            "BioMed Black Resin","Custom Tray Resin","IBT Resin","Precision Model Resin",
            "Castable Wax 40 Resin","Castable Wax Resin","Silicone 40A Resin","Alumina 4N Resin"
        ],
        "單價": [6900,6900,6900,6900,6900,6900,8500,8500,8500,8500,12000,8500,
                 9500,9500,11000,12000,12000,13500,13500,13500,13500,13500,13500,
                 8500,15000,15000,18000,25000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()
PRINTERS = {
    "Form 4":  {"w": 200.0, "d": 125.0, "h": 210.0, "layer_time_sec": 5.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0, "layer_time_sec": 6.0},
}

# --- 4. 產生給 Three.js 用的 JSON 幾何資料（取代 GLB）---
def mesh_to_threejs_json(mesh, printer_box, qty, off_x, off_y, thin_faces=None):
    """
    回傳一個 dict，包含：
      - parts: 零件頂點+面+顏色（逐 face 展開，適合 BufferGeometry）
      - box: 印表機邊框 wireframe 的 12 條線段端點
      - printer: 機台尺寸
      - is_over: 是否超出範圍
    """
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    cols = max(1, int(np.ceil(np.sqrt(qty))))
    spacing = mesh.extents[0] * 1.15

    all_positions = []
    all_colors = []

    thin_set = set(thin_faces) if thin_faces else set()

    for i in range(qty):
        m = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2)*spacing + off_x
        ty = (r - (cols-1)/2)*spacing + off_y
        tz = -m.bounds[0][2]   # 貼齊 z=0（Three.js 底面）
        m.apply_translation([tx, ty, tz])

        verts = m.vertices
        faces = m.faces

        for fi, face in enumerate(faces):
            for vi in face:
                v = verts[vi]
                all_positions.extend([float(v[0]), float(v[2]), float(-v[1])])  # Y-up 轉換
                if fi in thin_set:
                    all_colors.extend([1.0, 0.18, 0.18])   # 紅色薄壁
                else:
                    all_colors.extend([0.0, 0.506, 1.0])   # PreForm 藍

    # 邊界檢測（用原始座標）
    instances_bounds = []
    for i in range(qty):
        m = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2)*spacing + off_x
        ty = (r - (cols-1)/2)*spacing + off_y
        tz = -m.bounds[0][2]
        m.apply_translation([tx, ty, tz])
        instances_bounds.append(m.bounds)

    all_b = np.array(instances_bounds)
    mn = all_b[:, 0, :].min(axis=0)
    mx = all_b[:, 1, :].max(axis=0)
    is_over = bool(
        mn[0] < -w/2 or mx[0] > w/2 or
        mn[1] < -d/2 or mx[1] > d/2 or
        mx[2] > h
    )

    return {
        "positions": all_positions,
        "colors": all_colors,
        "printer": {"w": w, "d": d, "h": h},
        "is_over": is_over,
        "offset": [off_x, off_y]
    }


# --- 5. PreForm 風格 Three.js 渲染器（完整 HTML）---
def preform_viewer_html(geo_json: dict) -> str:
    data_str = json.dumps(geo_json)
    is_over = geo_json["is_over"]
    box_color = "#e11d48" if is_over else "#94a3b8"

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#1e2433; font-family: 'Segoe UI', sans-serif; overflow:hidden; }}

  #canvas-wrap {{
    position: relative;
    width: 100%;
    height: 580px;
  }}
  canvas {{ display:block; width:100%!important; height:100%!important; }}

  /* ── PreForm 頂部視角工具列 ── */
  #viewbar {{
    position:absolute; top:10px; left:50%; transform:translateX(-50%);
    display:flex; gap:4px; background:rgba(15,23,42,0.85);
    border:1px solid #334155; border-radius:6px; padding:4px 6px;
    backdrop-filter:blur(4px); z-index:10;
  }}
  .vbtn {{
    background:transparent; border:1px solid transparent;
    color:#94a3b8; font-size:11px; font-weight:600;
    padding:3px 9px; border-radius:4px; cursor:pointer;
    white-space:nowrap; transition:all .15s;
  }}
  .vbtn:hover {{ background:#1e40af; color:#fff; border-color:#3b82f6; }}
  .vbtn.active {{ background:#0081FF; color:#fff; border-color:#0081FF; }}
  .vdivider {{ width:1px; background:#334155; margin:2px 2px; }}

  /* ── 右下角操作提示 ── */
  #hint {{
    position:absolute; bottom:10px; right:12px;
    font-size:10px; color:#64748b; line-height:1.7;
    text-align:right; pointer-events:none;
  }}
  #hint span {{ color:#94a3b8; }}

  /* ── 左上角資訊面板 ── */
  #info {{
    position:absolute; top:10px; left:10px;
    background:rgba(15,23,42,0.85); border:1px solid #1e3a5f;
    border-radius:6px; padding:8px 12px; font-size:11px;
    color:#7dd3fc; line-height:1.8; pointer-events:none;
    backdrop-filter:blur(4px);
  }}
  #info .label {{ color:#475569; font-size:9px; text-transform:uppercase; }}

  /* ── 超出範圍警示 ── */
  #over-badge {{
    display:{'flex' if is_over else 'none'};
    position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
    background:#fef2f2; border:1px solid #fca5a5; border-radius:5px;
    color:#dc2626; font-size:11px; font-weight:700;
    padding:4px 14px; gap:6px; align-items:center;
  }}
</style>
</head>
<body>
<div id="canvas-wrap">
  <canvas id="c"></canvas>

  <!-- 頂部視角工具列（模擬 PreForm） -->
  <div id="viewbar">
    <button class="vbtn" onclick="setView('home')" title="重置視角 (F)">⌂ Home</button>
    <div class="vdivider"></div>
    <button class="vbtn" id="btn-persp" onclick="setView('persp')" title="透視圖">透視</button>
    <button class="vbtn" id="btn-top"   onclick="setView('top')"   title="俯視圖 (T)">俯視</button>
    <button class="vbtn" id="btn-front" onclick="setView('front')" title="正視圖">正視</button>
    <button class="vbtn" id="btn-right" onclick="setView('right')" title="右視圖">右視</button>
    <button class="vbtn" id="btn-iso"   onclick="setView('iso')"   title="等角視圖">等角</button>
    <div class="vdivider"></div>
    <button class="vbtn" onclick="toggleWire()" id="btn-wire" title="切換線框">線框</button>
    <button class="vbtn" onclick="fitAll()"     title="全部顯示 (F)">⊡ Fit</button>
  </div>

  <!-- 左上資訊 -->
  <div id="info">
    <div class="label">Printer</div>
    <div id="info-printer">—</div>
    <div class="label" style="margin-top:4px">Cursor</div>
    <div id="info-cursor">—</div>
  </div>

  <!-- 超出範圍 -->
  <div id="over-badge">⚠ 零件超出列印範圍，請調整位置或縮小數量</div>

  <!-- 右下提示 -->
  <div id="hint">
    <span>右鍵拖曳</span> 旋轉視角<br>
    <span>Shift＋右鍵</span> 平移<br>
    <span>滾輪</span> 縮放<br>
    <span>F</span> 重置視角
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ════════════════════════════════════════════════
//  資料注入
// ════════════════════════════════════════════════
const GEO = {data_str};
const W = GEO.printer.w, D = GEO.printer.d, H = GEO.printer.h;

// ════════════════════════════════════════════════
//  Scene / Camera / Renderer
// ════════════════════════════════════════════════
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({{ canvas, antialias:true, alpha:true }});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a2235);

// 霧氣（PreForm 深色背景質感）
scene.fog = new THREE.FogExp2(0x1a2235, 0.0008);

const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50000);

// ════════════════════════════════════════════════
//  燈光（模擬 PreForm 柔和工作室光）
// ════════════════════════════════════════════════
scene.add(new THREE.AmbientLight(0xffffff, 0.55));

const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight1.position.set(W, H*2, D);
dirLight1.castShadow = true;
scene.add(dirLight1);

const dirLight2 = new THREE.DirectionalLight(0x8cb4ff, 0.35);
dirLight2.position.set(-W, H, -D);
scene.add(dirLight2);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.2);
fillLight.position.set(0, -H, 0);
scene.add(fillLight);

// ════════════════════════════════════════════════
//  地板網格（PreForm 深灰風格）
// ════════════════════════════════════════════════
const gridHelper = new THREE.GridHelper(Math.max(W,D)*2, 20, 0x2d3748, 0x232f40);
gridHelper.position.set(0, 0, 0);
scene.add(gridHelper);

// 印表機底部平面（半透明）
const floorGeo = new THREE.PlaneGeometry(W, D);
const floorMat = new THREE.MeshStandardMaterial({{
  color: 0x0f172a, transparent:true, opacity:0.5,
  roughness:0.9, metalness:0.1
}});
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI/2;
floor.receiveShadow = true;
scene.add(floor);

// ════════════════════════════════════════════════
//  印表機邊框 Wireframe
// ════════════════════════════════════════════════
const boxColor = GEO.is_over ? 0xe11d48 : 0x475569;
const boxMat = new THREE.LineBasicMaterial({{ color: boxColor, linewidth: 1 }});
const hw=W/2, hd=D/2;
const bv = [
  [-hw,-hd, 0],[hw,-hd, 0],[hw, hd, 0],[-hw, hd, 0],
  [-hw,-hd, H],[hw,-hd, H],[hw, hd, H],[-hw, hd, H]
];
const edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],
               [0,4],[1,5],[2,6],[3,7]];
edges.forEach(([a,b]) => {{
  const g = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(...bv[a]), new THREE.Vector3(...bv[b])
  ]);
  scene.add(new THREE.Line(g, boxMat));
}});

// 角落尺寸標示小平面（PreForm 特色）
const cornerMat = new THREE.MeshBasicMaterial({{ color: boxColor, transparent:true, opacity:0.15 }});
[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]].forEach(([a,b,c,dd]) => {{
  const pg = new THREE.BufferGeometry();
  const pts = [bv[a],bv[b],bv[c],bv[dd]];
  pg.setAttribute('position', new THREE.BufferAttribute(
    new Float32Array(pts.flat()), 3));
  pg.setIndex([0,1,2, 0,2,3]);
  scene.add(new THREE.Mesh(pg, cornerMat));
}});

// ════════════════════════════════════════════════
//  零件 Mesh（BufferGeometry + vertexColors）
// ════════════════════════════════════════════════
let partMesh, wireframeMesh;
let showWire = false;

function buildPart() {{
  if(partMesh) scene.remove(partMesh);
  if(wireframeMesh) scene.remove(wireframeMesh);

  const pos = new Float32Array(GEO.positions);
  const col = new Float32Array(GEO.colors);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color',    new THREE.BufferAttribute(col, 3));
  geo.computeVertexNormals();

  const mat = new THREE.MeshPhongMaterial({{
    vertexColors: true,
    transparent: true,
    opacity: 0.88,
    shininess: 60,
    specular: new THREE.Color(0x224488),
    side: THREE.DoubleSide
  }});
  partMesh = new THREE.Mesh(geo, mat);
  partMesh.castShadow = true;
  partMesh.receiveShadow = true;
  scene.add(partMesh);

  // 線框覆蓋
  const wMat = new THREE.MeshBasicMaterial({{
    color: 0x93c5fd, wireframe:true, transparent:true, opacity:0.12
  }});
  wireframeMesh = new THREE.Mesh(geo, wMat);
  wireframeMesh.visible = showWire;
  scene.add(wireframeMesh);
}}
buildPart();

function toggleWire() {{
  showWire = !showWire;
  wireframeMesh.visible = showWire;
  document.getElementById('btn-wire').classList.toggle('active', showWire);
}}

// ════════════════════════════════════════════════
//  視角控制（PreForm 操作慣例）
//  右鍵拖曳 → Orbit | Shift+右鍵 → Pan | 滾輪 → Zoom
// ════════════════════════════════════════════════
const TARGET = new THREE.Vector3(0, H/2, 0);   // 預設看向機台中心
let isDragging = false, isShift = false;
let lastX = 0, lastY = 0;
let spherical = new THREE.Spherical();
let panOffset = new THREE.Vector3();

function updateCamera() {{
  const pos = new THREE.Vector3().setFromSpherical(spherical);
  pos.add(TARGET).add(panOffset);
  camera.position.copy(pos);
  camera.lookAt(TARGET.clone().add(panOffset));
}}

// 初始等角視角
function setView(name) {{
  const R = spherical.radius;
  panOffset.set(0,0,0);
  document.querySelectorAll('.vbtn[id^=btn-]').forEach(b=>b.classList.remove('active'));
  switch(name) {{
    case 'persp':
      spherical.set(R, Math.PI/4, Math.PI/6);
      document.getElementById('btn-persp')?.classList.add('active'); break;
    case 'top':
      spherical.set(R, 0.01, 0);
      document.getElementById('btn-top')?.classList.add('active'); break;
    case 'front':
      spherical.set(R, Math.PI/2, 0);
      document.getElementById('btn-front')?.classList.add('active'); break;
    case 'right':
      spherical.set(R, Math.PI/2, Math.PI/2);
      document.getElementById('btn-right')?.classList.add('active'); break;
    case 'iso':
      spherical.set(R, Math.PI/4, Math.PI/4);
      document.getElementById('btn-iso')?.classList.add('active'); break;
    case 'home':
    default:
      spherical.set(R, Math.PI/4, Math.PI/6);
      break;
  }}
  updateCamera();
}}

function fitAll() {{
  const size = Math.max(W, D, H);
  spherical.radius = size * 2.2;
  setView('home');
}}

// 初始化視角
spherical.set(Math.max(W,D,H)*2.2, Math.PI/4, Math.PI/6);
updateCamera();
document.getElementById('btn-iso')?.classList.add('active');
document.getElementById('info-printer').textContent = GEO.printer.w+'×'+GEO.printer.d+'×'+GEO.printer.h+' mm';

// 滑鼠事件
canvas.addEventListener('contextmenu', e => e.preventDefault());

canvas.addEventListener('mousedown', e => {{
  if(e.button === 2) {{
    isDragging = true;
    isShift = e.shiftKey;
    lastX = e.clientX;
    lastY = e.clientY;
  }}
}});

window.addEventListener('mouseup', () => isDragging = false);

window.addEventListener('mousemove', e => {{
  if(!isDragging) {{
    // 顯示游標座標
    const rect = canvas.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / rect.width  * 2 - 1;
    const ny = -(e.clientY - rect.top)  / rect.height * 2 + 1;
    document.getElementById('info-cursor').textContent =
      (nx*W/2).toFixed(1)+', '+(ny*D/2).toFixed(1)+' mm';
    return;
  }}

  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;

  if(isShift || e.shiftKey) {{
    // Pan（Shift＋右鍵）
    const panSpeed = spherical.radius * 0.001;
    const right = new THREE.Vector3();
    const up = new THREE.Vector3();
    camera.getWorldDirection(new THREE.Vector3());
    right.crossVectors(camera.getWorldDirection(new THREE.Vector3()),
                       camera.up).normalize();
    up.copy(camera.up).normalize();
    panOffset.addScaledVector(right, -dx * panSpeed);
    panOffset.addScaledVector(up,     dy * panSpeed);
  }} else {{
    // Orbit（右鍵）
    spherical.theta -= dx * 0.008;
    spherical.phi   -= dy * 0.008;
    spherical.phi = Math.max(0.05, Math.min(Math.PI - 0.05, spherical.phi));
  }}
  updateCamera();
}});

// 滾輪縮放（PreForm 預設：往上滾 = 縮小，往下 = 放大，但可逆）
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  const factor = e.deltaY > 0 ? 1.1 : 0.9;
  spherical.radius = Math.max(10, Math.min(spherical.radius * factor, 50000));
  updateCamera();
}}, {{ passive:false }});

// 鍵盤
window.addEventListener('keydown', e => {{
  if(e.key === 'f' || e.key === 'F') fitAll();
  if(e.key === 't' || e.key === 'T') setView('top');
}});

// ════════════════════════════════════════════════
//  Resize
// ════════════════════════════════════════════════
function resize() {{
  const w = canvas.parentElement.clientWidth;
  const h = canvas.parentElement.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w/h;
  camera.updateProjectionMatrix();
}}
window.addEventListener('resize', resize);
resize();

// ════════════════════════════════════════════════
//  Render Loop
// ════════════════════════════════════════════════
(function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}})();
</script>
</body>
</html>
"""


# ════════════════════════════════════════════════
#  側邊欄
# ════════════════════════════════════════════════
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=20)
    st.title("PreForm 模擬報價")

    st.markdown('<div class="priority-note">📌 上傳 STL 優先；未上傳時使用手動體積估算。</div>',
                unsafe_allow_html=True)

    with st.container():
        st.subheader("⌨️ 手動估價")
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("體積值", min_value=0.0, step=100.0)

    with st.container():
        st.subheader("📂 上傳 STL 檔案")
        up_file = st.file_uploader("STL 檔案（優先使用）", type=["stl"])

    st.divider()
    m_choice  = st.selectbox("Formlabs 材料選擇", df_m["材料名稱"].tolist())
    p_choice  = st.selectbox("列印機型範圍", list(PRINTERS.keys()))
    qty       = st.number_input("數量", min_value=1, value=1)
    markup    = st.number_input("報價加成倍率", min_value=1.0, value=2.0)

    st.divider()
    st.subheader("⚙️ 進階設定")
    support_ratio  = st.slider("支撐結構體積係數 (%)", 0, 50, 20, 5,
                                help="SLA 通常需要額外 15~30% 支撐材料。")
    layer_thickness = st.selectbox("層厚 (mm)", [0.05, 0.1, 0.2], index=1)
    min_t_val       = st.slider("薄度偵測閾值 (mm)", 0.0, 5.0, 0.5, 0.5)
    handling_fee    = st.number_input("基本處理費 / 件 (NT$)", min_value=0, value=200, step=50,
                                       help="含清洗、後固化等後處理成本。")


# ════════════════════════════════════════════════
#  主畫面
# ════════════════════════════════════════════════
u_cost       = df_m.loc[df_m["材料名稱"]==m_choice, "每mm3成本"].values[0]
printer_spec = PRINTERS[p_choice]

# 用 MD5 hash 判斷檔案是否改變
if up_file:
    file_bytes = up_file.read()
    file_hash  = hashlib.md5(file_bytes).hexdigest()
    if st.session_state.mesh_hash != file_hash:
        st.session_state.mesh       = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        st.session_state.mesh_hash  = file_hash
        st.session_state.offset     = [0.0, 0.0]
        st.session_state.thin_faces = None

use_stl    = up_file and st.session_state.mesh is not None
use_manual = not use_stl and manual_v > 0

if use_stl or use_manual:
    model_vol = st.session_state.mesh.volume if use_stl else \
                (manual_v if m_unit=="mm³" else manual_v*1000)

    # 成本計算
    support_vol          = model_vol * (support_ratio/100)
    total_vol_per_unit   = model_vol + support_vol
    material_cost_total  = total_vol_per_unit * u_cost * qty
    handling_total       = handling_fee * qty
    subtotal             = material_cost_total + handling_total
    final_price          = subtotal * markup

    # 列印時間估算
    model_h     = st.session_state.mesh.extents[2] if use_stl else model_vol**(1/3)
    n_layers    = int(np.ceil(model_h / layer_thickness))
    print_time  = (n_layers * printer_spec["layer_time_sec"]) / 60

    # 報價看板
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size:13px;color:#64748b;font-weight:bold;margin-bottom:4px;">PREFORM 預估總列印成本</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">模型體積</div><div class="data-value">{model_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">含支撐消耗 (mL)</div><div class="data-value">{total_vol_per_unit*qty/1000:,.2f}</div></div>
            <div class="data-item"><div class="data-label">列印機型</div><div class="data-value">{p_choice}</div></div>
            <div class="data-item"><div class="data-label">預估列印時間</div><div class="data-value">≈ {print_time:.0f} 分鐘</div></div>
            <div class="data-item"><div class="data-label">層數（{layer_thickness}mm）</div><div class="data-value">{n_layers:,} 層</div></div>
        </div>
        <div class="cost-breakdown">
            <div class="cost-row">
                <span>材料費（含支撐 {support_ratio}%，{total_vol_per_unit/1000:.2f} mL/件）× {qty} 件</span>
                <span>NT$ {material_cost_total:,.0f}</span>
            </div>
            <div class="cost-row">
                <span>後處理費（NT$ {handling_fee}/件）× {qty} 件</span>
                <span>NT$ {handling_total:,.0f}</span>
            </div>
            <div class="cost-row"><span>小計</span><span>NT$ {subtotal:,.0f}</span></div>
            <div class="cost-row total"><span>× 加成 {markup}x　→　最終報價</span><span>NT$ {final_price:,.0f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3D 操作區（STL 模式）
    if use_stl:
        st.divider()
        col_tool, col_view = st.columns([1, 3])

        with col_tool:
            st.write("🕹️ 零件操作")

            if st.button("✨ SLA 45° 擺放建議"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45),[1,1,0])
                st.session_state.mesh.apply_transform(rot)
                st.session_state.thin_faces = None
                st.rerun()

            if st.button("🔴 薄度偵測分析"):
                mesh = st.session_state.mesh
                tree = cKDTree(mesh.triangles_center)
                thin_set = set()
                for fi,(center,normal) in enumerate(zip(mesh.triangles_center, mesh.face_normals)):
                    dists,idxs = tree.query(center, k=6)
                    for dist,nfi in zip(dists[1:],idxs[1:]):
                        if dist < min_t_val and np.dot(normal, mesh.face_normals[nfi]) < -0.5:
                            thin_set.add(fi); break
                st.session_state.thin_faces = thin_set
                if thin_set:
                    st.warning(f"⚠️ 偵測到 {len(thin_set)} 個薄壁面（< {min_t_val}mm）")
                else:
                    st.success(f"✅ 無薄壁問題（閾值 {min_t_val}mm）")

            if st.button("🔵 清除薄度標記"):
                st.session_state.thin_faces = None
                st.rerun()

            st.write("📏 X/Y 位置調整")
            c1,c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3,c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()

            if st.button("🔄 旋轉 90°"):
                st.session_state.mesh.apply_transform(
                    trimesh.transformations.rotation_matrix(np.radians(90),[0,0,1]))
                st.session_state.thin_faces = None
                st.rerun()

            if st.button("🏠 重置位置"):
                st.session_state.offset = [0.0, 0.0]
                st.rerun()

        with col_view:
            # 產生 Three.js 需要的幾何 JSON
            geo_json = mesh_to_threejs_json(
                st.session_state.mesh,
                printer_spec, qty,
                st.session_state.offset[0],
                st.session_state.offset[1],
                thin_faces=st.session_state.thin_faces
            )

            html_code = preform_viewer_html(geo_json)
            st.components.v1.html(html_code, height=600, scrolling=False)

else:
    st.info("💡 請上傳 STL 模型（左側），或手動輸入體積，開始 PreForm 專業模擬。")
    st.markdown("""
**使用說明：**
- 📂 **上傳 STL**：自動計算體積，支援 3D 排版與薄度偵測（優先使用）
- ⌨️ **手動輸入**：僅輸入體積時使用，適合快速估算
- ⚙️ **進階設定**：可調整支撐係數、層厚、後處理費用

**3D 視窗操作（PreForm 慣例）：**
| 動作 | 效果 |
|------|------|
| 右鍵拖曳 | 旋轉視角 |
| Shift＋右鍵拖曳 | 平移畫面 |
| 滾輪 | 縮放 |
| F 鍵 | 重置視角 |
| 頂部工具列 | 切換俯視／正視／等角等標準視角 |
    """)
