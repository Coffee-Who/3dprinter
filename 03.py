import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
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
for k, v in [('offset', [0.0, 0.0]), ('mesh', None), ('mesh_hash', ""), ('thin_faces', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# --- 3. 材料與設備規格 ---
@st.cache_data
def load_materials():
    data = {
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Draft Resin V2", "Model Resin V3", "Tough 2000 Resin", "Tough 1500 Resin",
            "Durable Resin", "Grey Pro Resin", "Rigid 10K Resin", "Rigid 4000 Resin",
            "Flexible 80A Resin", "Elastic 50A Resin", "High Temp Resin", "Flame Retardant Resin",
            "ESD Resin", "BioMed Clear Resin", "BioMed Amber Resin", "BioMed White Resin",
            "BioMed Black Resin", "Custom Tray Resin", "IBT Resin", "Precision Model Resin",
            "Castable Wax 40 Resin", "Castable Wax Resin", "Silicone 40A Resin", "Alumina 4N Resin"
        ],
        "單價": [6900, 6900, 6900, 6900, 6900, 6900, 8500, 8500, 8500, 8500, 12000, 8500,
                 9500, 9500, 11000, 12000, 12000, 13500, 13500, 13500, 13500, 13500, 13500,
                 8500, 15000, 15000, 18000, 25000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()

# 尺寸單位：mm
# Three.js 座標系：X=寬(W), Y=高(H，向上), Z=深(D)
# 框線：底面在 Y=0，中心在 XZ 原點
# 所以框線範圍：X ∈ [-W/2, W/2], Z ∈ [-D/2, D/2], Y ∈ [0, H]
PRINTERS = {
    "Form 4":  {"w": 200.0, "d": 125.0, "h": 210.0, "layer_time_sec": 5.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0, "layer_time_sec": 6.0},
}


# --- 4. 產生給 Three.js 的幾何 JSON ---
# 座標轉換規則（trimesh → Three.js）:
#   Three.js X = trimesh X
#   Three.js Y = trimesh Z  (高度)
#   Three.js Z = trimesh Y  (深度，注意正負)
# 零件底部貼齊 Three.js Y=0（框線底部），XZ 置中在框線中心
def mesh_to_threejs_json(mesh, printer_box, qty, off_x, off_y, thin_faces=None):
    W = printer_box['w']
    D = printer_box['d']
    H = printer_box['h']

    cols = max(1, int(np.ceil(np.sqrt(qty))))
    rows = max(1, int(np.ceil(qty / cols)))

    # 間距用模型最大水平邊長 * 1.15
    sx = mesh.extents[0] * 1.15   # trimesh X 方向
    sy = mesh.extents[1] * 1.15   # trimesh Y 方向

    all_positions = []
    all_colors = []
    thin_set = set(thin_faces) if thin_faces else set()

    # 計算所有 instance 的 trimesh 座標，底部貼齊 Z=0，XY 陣列置中
    for i in range(qty):
        m = mesh.copy()
        r, c = divmod(i, cols)

        # 讓陣列在 trimesh XY 平面置中
        tx = (c - (cols - 1) / 2.0) * sx + off_x
        ty = (r - (rows - 1) / 2.0) * sy + off_y
        tz = -m.bounds[0][2]   # 底部貼齊 trimesh Z=0

        m.apply_translation([tx, ty, tz])
        verts = m.vertices
        faces = m.faces

        for fi, face in enumerate(faces):
            for vi in face:
                v = verts[vi]
                # trimesh(X,Y,Z) → Three.js(X, Z, -Y) 讓底部在 Three.js Y=0
                all_positions.extend([float(v[0]), float(v[2]), float(-v[1])])
                if fi in thin_set:
                    all_colors.extend([1.0, 0.18, 0.18])
                else:
                    all_colors.extend([0.0, 0.506, 1.0])

    # 邊界檢測（trimesh 空間，框線底面 trimesh Z=0, 頂面 Z=H, XY ±W/2, ±D/2）
    is_over = False
    for i in range(qty):
        m = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols - 1) / 2.0) * sx + off_x
        ty = (r - (rows - 1) / 2.0) * sy + off_y
        tz = -m.bounds[0][2]
        m.apply_translation([tx, ty, tz])
        b = m.bounds
        if (b[0][0] < -W/2 or b[1][0] > W/2 or
                b[0][1] < -D/2 or b[1][1] > D/2 or
                b[1][2] > H):
            is_over = True
            break

    return {
        "positions": all_positions,
        "colors": all_colors,
        "printer": {"w": W, "d": D, "h": H},
        "is_over": is_over,
        "thin_count": len(thin_set)
    }


# --- 5. PreForm 風格 Three.js 渲染器 ---
def preform_viewer_html(geo_json: dict) -> str:
    data_str = json.dumps(geo_json)
    is_over = geo_json["is_over"]
    thin_count = geo_json.get("thin_count", 0)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#1a2235; font-family:'Segoe UI',sans-serif; overflow:hidden; }}
#wrap {{ position:relative; width:100%; height:580px; }}
canvas {{ display:block; width:100%!important; height:100%!important; }}

/* 頂部視角工具列 */
#viewbar {{
  position:absolute; top:10px; left:50%; transform:translateX(-50%);
  display:flex; gap:3px; background:rgba(10,18,35,0.90);
  border:1px solid #2d3f5a; border-radius:6px; padding:4px 6px;
  backdrop-filter:blur(6px); z-index:10; white-space:nowrap;
}}
.vbtn {{
  background:transparent; border:1px solid transparent;
  color:#7a9cc0; font-size:11px; font-weight:600;
  padding:3px 10px; border-radius:4px; cursor:pointer; transition:all .15s;
}}
.vbtn:hover  {{ background:#1e3a6e; color:#fff; border-color:#3b82f6; }}
.vbtn.active {{ background:#0081FF; color:#fff; border-color:#0081FF; }}
.sep {{ width:1px; background:#2d3f5a; margin:2px 2px; }}

/* 左上資訊面板 */
#info {{
  position:absolute; top:10px; left:10px;
  background:rgba(10,18,35,0.88); border:1px solid #1e3a5f;
  border-radius:6px; padding:8px 12px; font-size:11px;
  color:#7dd3fc; line-height:1.9; pointer-events:none;
  backdrop-filter:blur(4px);
}}
#info .lbl {{ color:#3d5a7a; font-size:9px; text-transform:uppercase; letter-spacing:.06em; }}

/* 右下操作提示 */
#hint {{
  position:absolute; bottom:10px; right:12px;
  font-size:10px; color:#3d5a7a; line-height:1.8;
  text-align:right; pointer-events:none;
}}
#hint b {{ color:#6b8fb5; }}

/* 超出範圍警示 */
#over-badge {{
  display:none; position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
  background:rgba(220,38,38,0.15); border:1px solid #f87171; border-radius:5px;
  color:#fca5a5; font-size:11px; font-weight:700; padding:5px 16px;
}}
#thin-badge {{
  display:none; position:absolute; bottom:40px; left:50%; transform:translateX(-50%);
  background:rgba(234,88,12,0.15); border:1px solid #fb923c; border-radius:5px;
  color:#fdba74; font-size:11px; font-weight:600; padding:4px 14px;
}}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c"></canvas>

  <div id="viewbar">
    <button class="vbtn" onclick="resetView()" title="重置 (F)">⌂ Home</button>
    <div class="sep"></div>
    <button class="vbtn" id="b-iso"   onclick="setView('iso')">等角</button>
    <button class="vbtn" id="b-top"   onclick="setView('top')">俯視</button>
    <button class="vbtn" id="b-front" onclick="setView('front')">正視</button>
    <button class="vbtn" id="b-right" onclick="setView('right')">右視</button>
    <div class="sep"></div>
    <button class="vbtn" id="b-wire"  onclick="toggleWire()">線框</button>
    <button class="vbtn" onclick="fitAll()">⊡ Fit</button>
  </div>

  <div id="info">
    <div class="lbl">Printer</div>
    <div id="i-printer">—</div>
    <div class="lbl" style="margin-top:3px">Volume (model)</div>
    <div id="i-vol">—</div>
  </div>

  <div id="over-badge">⚠ 零件超出列印範圍</div>
  <div id="thin-badge">🔴 薄壁標記顯示中</div>

  <div id="hint">
    <b>右鍵拖曳</b> 旋轉<br>
    <b>Shift＋右鍵</b> 平移<br>
    <b>滾輪</b> 縮放<br>
    <b>F</b> 重置視角
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── 注入資料 ──────────────────────────────────────
const GEO = {data_str};
const W = GEO.printer.w;   // mm, Three.js X 方向
const D = GEO.printer.d;   // mm, Three.js Z 方向
const H = GEO.printer.h;   // mm, Three.js Y 方向（向上）

// ── Renderer ──────────────────────────────────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({{ canvas, antialias:true }});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111827);

// ── Camera ────────────────────────────────────────
const camera = new THREE.PerspectiveCamera(32, 1, 0.5, 100000);

// ── 燈光 ──────────────────────────────────────────
scene.add(new THREE.AmbientLight(0xffffff, 0.50));
const sun = new THREE.DirectionalLight(0xffffff, 0.85);
sun.position.set(W, H * 2.5, D);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);
const fill = new THREE.DirectionalLight(0x9ab8e0, 0.40);
fill.position.set(-W * 0.8, H * 0.5, -D * 0.8);
scene.add(fill);
const bottom = new THREE.DirectionalLight(0x3a5070, 0.20);
bottom.position.set(0, -H, 0);
scene.add(bottom);

// ── 框線（Three.js 座標）────────────────────────
//    底面在 Y=0, 頂面在 Y=H
//    XZ 以原點置中：X ∈ [-W/2, W/2], Z ∈ [-D/2, D/2]
const hw = W / 2, hd = D / 2;

const isOver = GEO.is_over;
const boxHex = isOver ? 0xe11d48 : 0x4b6a8a;
const boxMat = new THREE.LineBasicMaterial({{ color: boxHex }});

// 12 條邊
const BV = [
  new THREE.Vector3(-hw, 0,  -hd), new THREE.Vector3( hw, 0,  -hd),
  new THREE.Vector3( hw, 0,   hd), new THREE.Vector3(-hw, 0,   hd),
  new THREE.Vector3(-hw, H,  -hd), new THREE.Vector3( hw, H,  -hd),
  new THREE.Vector3( hw, H,   hd), new THREE.Vector3(-hw, H,   hd),
];
[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
  .forEach(([a,b]) => {{
    const g = new THREE.BufferGeometry().setFromPoints([BV[a], BV[b]]);
    scene.add(new THREE.Line(g, boxMat));
  }});

// 側面半透明填色（視覺輔助）
const sideMat = new THREE.MeshBasicMaterial({{
  color: boxHex, transparent:true, opacity: isOver ? 0.08 : 0.04,
  side: THREE.DoubleSide, depthWrite:false
}});
[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]].forEach(([a,b,c,d]) => {{
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(
    new Float32Array([...BV[a].toArray(),...BV[b].toArray(),
                      ...BV[c].toArray(),...BV[d].toArray()]), 3));
  g.setIndex([0,1,2, 0,2,3]);
  scene.add(new THREE.Mesh(g, sideMat));
}});

// ── 底部格子（框線底面範圍內）────────────────────
// 格子線只在 X ∈ [-W/2,W/2], Z ∈ [-D/2,D/2], Y=0
const gridMat = new THREE.LineBasicMaterial({{ color:0x1e3a55, transparent:true, opacity:0.9 }});
const gridMajMat = new THREE.LineBasicMaterial({{ color:0x2a5a80, transparent:true, opacity:0.7 }});

function makeGrid() {{
  // 格線間距：讓格子數約 10~14 格
  const rawStep = Math.max(W, D) / 12;
  // 取整到 5mm 的倍數
  const step = Math.ceil(rawStep / 5) * 5;

  // X 方向線（沿 Z 延伸）
  for(let x = -hw; x <= hw + 0.01; x += step) {{
    const xc = Math.round(x / step) * step;
    if(xc < -hw || xc > hw) continue;
    const isMaj = Math.abs(xc % (step * 2)) < 0.01;
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(xc, 0, -hd),
      new THREE.Vector3(xc, 0,  hd)
    ]);
    scene.add(new THREE.Line(g, isMaj ? gridMajMat : gridMat));
  }}
  // Z 方向線（沿 X 延伸）
  for(let z = -hd; z <= hd + 0.01; z += step) {{
    const zc = Math.round(z / step) * step;
    if(zc < -hd || zc > hd) continue;
    const isMaj = Math.abs(zc % (step * 2)) < 0.01;
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-hw, 0, zc),
      new THREE.Vector3( hw, 0, zc)
    ]);
    scene.add(new THREE.Line(g, isMaj ? gridMajMat : gridMat));
  }}

  // 底部填色平面
  const floorGeo = new THREE.PlaneGeometry(W, D);
  const floorMat = new THREE.MeshStandardMaterial({{
    color: 0x0a1628, transparent:true, opacity:0.70,
    roughness:1, metalness:0, depthWrite:false
  }});
  const floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;   // 水平
  floorMesh.position.y = 0.01;           // 略高於 Y=0 避免 z-fighting
  floorMesh.receiveShadow = true;
  scene.add(floorMesh);
}}
makeGrid();

// ── 零件 Mesh ─────────────────────────────────────
let partMesh = null, wireMesh = null;
let wireOn = false;

function buildPart() {{
  if(partMesh)  scene.remove(partMesh);
  if(wireMesh)  scene.remove(wireMesh);
  if(!GEO.positions || GEO.positions.length === 0) return;

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(GEO.positions), 3));
  geo.setAttribute('color',    new THREE.BufferAttribute(new Float32Array(GEO.colors),    3));
  geo.computeVertexNormals();

  partMesh = new THREE.Mesh(geo, new THREE.MeshPhongMaterial({{
    vertexColors: true, transparent:true, opacity:0.90,
    shininess:55, specular:new THREE.Color(0x1a3a6a), side:THREE.DoubleSide
  }}));
  partMesh.castShadow = true;
  scene.add(partMesh);

  wireMesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({{
    color:0x7dd3fc, wireframe:true, transparent:true, opacity:0.10
  }}));
  wireMesh.visible = wireOn;
  scene.add(wireMesh);
}}
buildPart();

function toggleWire() {{
  wireOn = !wireOn;
  if(wireMesh) wireMesh.visible = wireOn;
  document.getElementById('b-wire').classList.toggle('active', wireOn);
}}

// ── UI 標示 ────────────────────────────────────────
if(isOver) document.getElementById('over-badge').style.display = 'block';
if(GEO.thin_count > 0) document.getElementById('thin-badge').style.display = 'block';
document.getElementById('i-printer').textContent =
  W + ' × ' + D + ' × ' + H + ' mm';
// 用頂點數反推大概體積（僅用於顯示）
document.getElementById('i-vol').textContent =
  (GEO.positions.length / 9).toLocaleString() + ' faces';

// ── 視角控制 ──────────────────────────────────────
// 使用球座標 Spherical (r, phi, theta) 繞 TARGET 點
// TARGET = 框線中心 (0, H/2, 0)
const TARGET = new THREE.Vector3(0, H / 2, 0);
const sph = new THREE.Spherical();
let panOff = new THREE.Vector3();

function updateCam() {{
  const p = new THREE.Vector3().setFromSpherical(sph);
  p.add(TARGET).add(panOff);
  camera.position.copy(p);
  camera.lookAt(TARGET.clone().add(panOff));
}}

function calcR() {{
  // 讓框線完整出現在視野內的距離
  const diag = Math.sqrt(W*W + D*D + H*H);
  const fovRad = camera.fov * Math.PI / 180;
  return (diag / 2) / Math.sin(fovRad / 2) * 1.45;
}}

// 標準等角視角：從右前上方看，phi≈54.7°, theta≈-45°（真正等角投影角度）
function resetView() {{
  sph.set(calcR(), Math.PI / 2 - Math.atan(1 / Math.sqrt(2)), -Math.PI / 4);
  panOff.set(0, 0, 0);
  setActive('b-iso');
  updateCam();
}}

function setView(name) {{
  const R = calcR();
  panOff.set(0, 0, 0);
  switch(name) {{
    case 'iso':
      sph.set(R, Math.PI/2 - Math.atan(1/Math.sqrt(2)), -Math.PI/4); break;
    case 'top':
      sph.set(R, 0.001, 0); break;
    case 'front':
      sph.set(R, Math.PI/2, 0); break;
    case 'right':
      sph.set(R, Math.PI/2, -Math.PI/2); break;
  }}
  setActive('b-'+name);
  updateCam();
}}

function fitAll() {{
  sph.radius = calcR();
  panOff.set(0, 0, 0);
  updateCam();
}}

function setActive(id) {{
  document.querySelectorAll('.vbtn[id^=b-]').forEach(b => b.classList.remove('active'));
  const el = document.getElementById(id);
  if(el) el.classList.add('active');
}}

// 初始視角
resetView();

// ── 滑鼠操作 ──────────────────────────────────────
let dragging = false, shiftDown = false, lastX = 0, lastY = 0;

canvas.addEventListener('contextmenu', e => e.preventDefault());

canvas.addEventListener('mousedown', e => {{
  if(e.button === 2) {{
    dragging = true;
    shiftDown = e.shiftKey;
    lastX = e.clientX; lastY = e.clientY;
  }}
}});
window.addEventListener('mouseup', () => {{ dragging = false; }});

window.addEventListener('mousemove', e => {{
  if(!dragging) return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX; lastY = e.clientY;

  if(shiftDown || e.shiftKey) {{
    // Pan：沿相機的 right / up 方向移動 TARGET
    const speed = sph.radius * 0.0012;
    const right = new THREE.Vector3();
    right.crossVectors(
      camera.getWorldDirection(new THREE.Vector3()), camera.up
    ).normalize();
    panOff.addScaledVector(right, -dx * speed);
    panOff.addScaledVector(camera.up, dy * speed);
  }} else {{
    // Orbit：右鍵拖曳旋轉
    sph.theta += dx * 0.007;
    sph.phi   -= dy * 0.007;
    sph.phi = Math.max(0.02, Math.min(Math.PI - 0.02, sph.phi));
  }}
  updateCam();
}});

// 滾輪縮放
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  sph.radius *= e.deltaY > 0 ? 1.10 : 0.91;
  sph.radius = Math.max(10, Math.min(sph.radius, 200000));
  updateCam();
}}, {{ passive:false }});

// 鍵盤快捷鍵
window.addEventListener('keydown', e => {{
  const k = e.key.toLowerCase();
  if(k === 'f') resetView();
  if(k === 't') setView('top');
  if(k === 'r') setView('right');
  if(k === 'i') setView('iso');
}});

// ── Resize ────────────────────────────────────────
function onResize() {{
  const w = canvas.parentElement.clientWidth;
  const h = canvas.parentElement.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}}
window.addEventListener('resize', onResize);
onResize();

// ── Render Loop ───────────────────────────────────
(function loop() {{
  requestAnimationFrame(loop);
  renderer.render(scene, camera);
}})();
</script>
</body>
</html>"""


# ════════════════════════════════════════════════
#  側邊欄
# ════════════════════════════════════════════════
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=20)
    st.title("PreForm 模擬報價")

    st.markdown(
        '<div class="priority-note">📌 上傳 STL 優先；未上傳時使用手動體積估算。</div>',
        unsafe_allow_html=True
    )

    with st.container():
        st.subheader("⌨️ 手動估價")
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("體積值", min_value=0.0, step=100.0)

    with st.container():
        st.subheader("📂 上傳 STL 檔案")
        up_file = st.file_uploader("STL 檔案（優先使用）", type=["stl"])

    st.divider()
    m_choice = st.selectbox("Formlabs 材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印機型範圍", list(PRINTERS.keys()))
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("報價加成倍率", min_value=1.0, value=2.0)

    st.divider()
    st.subheader("⚙️ 進階設定")
    support_ratio = st.slider("支撐結構體積係數 (%)", 0, 50, 20, 5,
                               help="SLA 通常需要額外 15~30% 支撐材料。")
    layer_thickness = st.selectbox("層厚 (mm)", [0.05, 0.1, 0.2], index=1)
    min_t_val = st.slider("薄度偵測閾值 (mm)", 0.0, 5.0, 0.5, 0.5)
    handling_fee = st.number_input("基本處理費 / 件 (NT$)", min_value=0, value=200, step=50,
                                    help="含清洗、後固化等後處理成本。")


# ════════════════════════════════════════════════
#  主畫面
# ════════════════════════════════════════════════
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
printer_spec = PRINTERS[p_choice]

# MD5 hash 判斷檔案是否真的改變
if up_file:
    file_bytes = up_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()
    if st.session_state.mesh_hash != file_hash:
        raw = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        # 將模型移到 trimesh 原點：底部貼齊 Z=0，XY 置中到框線中心
        raw.apply_translation(-raw.bounds[0])           # 底部到 Z=0
        raw.apply_translation([
            -raw.extents[0] / 2,                        # X 置中
            -raw.extents[1] / 2,                        # Y 置中
            0
        ])
        st.session_state.mesh = raw
        st.session_state.mesh_hash = file_hash
        st.session_state.offset = [0.0, 0.0]
        st.session_state.thin_faces = None

use_stl = up_file and st.session_state.mesh is not None
use_manual = not use_stl and manual_v > 0

if use_stl or use_manual:
    model_vol = st.session_state.mesh.volume if use_stl else \
                (manual_v if m_unit == "mm³" else manual_v * 1000)

    # 成本計算
    support_vol = model_vol * (support_ratio / 100)
    total_vol_per_unit = model_vol + support_vol
    material_cost_total = total_vol_per_unit * u_cost * qty
    handling_total = handling_fee * qty
    subtotal = material_cost_total + handling_total
    final_price = subtotal * markup

    # 列印時間估算
    model_h = st.session_state.mesh.extents[2] if use_stl else model_vol ** (1 / 3)
    n_layers = int(np.ceil(model_h / layer_thickness))
    print_time = (n_layers * printer_spec["layer_time_sec"]) / 60

    # 報價看板
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size:13px;color:#64748b;font-weight:bold;margin-bottom:4px;">PREFORM 預估總列印成本</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">模型體積</div><div class="data-value">{model_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">含支撐消耗 (mL)</div><div class="data-value">{total_vol_per_unit * qty / 1000:,.2f}</div></div>
            <div class="data-item"><div class="data-label">列印機型</div><div class="data-value">{p_choice}</div></div>
            <div class="data-item"><div class="data-label">預估列印時間</div><div class="data-value">≈ {print_time:.0f} 分鐘</div></div>
            <div class="data-item"><div class="data-label">層數（{layer_thickness}mm）</div><div class="data-value">{n_layers:,} 層</div></div>
        </div>
        <div class="cost-breakdown">
            <div class="cost-row">
                <span>材料費（含支撐 {support_ratio}%，{total_vol_per_unit / 1000:.2f} mL/件）× {qty} 件</span>
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

    # 3D 操作區
    if use_stl:
        st.divider()
        col_tool, col_view = st.columns([1, 3])

        with col_tool:
            st.write("🕹️ 零件操作")

            if st.button("✨ SLA 45° 擺放建議"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                # 重新貼齊底部並 XY 置中
                m = st.session_state.mesh
                m.apply_translation(-m.bounds[0])
                m.apply_translation([-m.extents[0]/2, -m.extents[1]/2, 0])
                st.session_state.thin_faces = None
                st.rerun()

            if st.button("🔴 薄度偵測分析"):
                mesh = st.session_state.mesh
                tree = cKDTree(mesh.triangles_center)
                thin_set = set()
                for fi, (center, normal) in enumerate(zip(mesh.triangles_center, mesh.face_normals)):
                    dists, idxs = tree.query(center, k=6)
                    for dist, nfi in zip(dists[1:], idxs[1:]):
                        if dist < min_t_val and np.dot(normal, mesh.face_normals[nfi]) < -0.5:
                            thin_set.add(fi)
                            break
                st.session_state.thin_faces = thin_set
                if thin_set:
                    st.warning(f"⚠️ 偵測到 {len(thin_set)} 個薄壁面（< {min_t_val}mm）")
                else:
                    st.success(f"✅ 無薄壁問題（閾值 {min_t_val}mm）")

            if st.button("🔵 清除薄度標記"):
                st.session_state.thin_faces = None
                st.rerun()

            st.write("📏 X/Y 位置微調")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()

            if st.button("🔄 旋轉 90°（Z 軸）"):
                m = st.session_state.mesh
                m.apply_transform(
                    trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
                )
                m.apply_translation(-m.bounds[0])
                m.apply_translation([-m.extents[0]/2, -m.extents[1]/2, 0])
                st.session_state.thin_faces = None
                st.rerun()

            if st.button("🏠 重置位置"):
                st.session_state.offset = [0.0, 0.0]
                st.rerun()

        with col_view:
            geo_json = mesh_to_threejs_json(
                st.session_state.mesh,
                printer_spec, qty,
                st.session_state.offset[0],
                st.session_state.offset[1],
                thin_faces=st.session_state.thin_faces
            )
            if geo_json["is_over"]:
                st.error("⚠️ 零件超出設備列印範圍！請調整位置或數量。")

            html_code = preform_viewer_html(geo_json)
            st.components.v1.html(html_code, height=600, scrolling=False)

else:
    st.info("💡 請上傳 STL 模型（左側），或手動輸入體積，開始 PreForm 專業模擬。")
    st.markdown("""
**使用說明：**
- 📂 **上傳 STL**：自動計算體積，支援 3D 排版與薄度偵測（優先使用）
- ⌨️ **手動輸入**：僅輸入體積時使用，適合快速估算

**3D 視窗操作：**

| 操作 | 效果 |
|------|------|
| 右鍵拖曳 | 旋轉視角 |
| Shift＋右鍵 | 平移畫面 |
| 滾輪 | 縮放 |
| F | 重置視角 |
| T / R / I | 俯視 / 右視 / 等角 |
    """)
