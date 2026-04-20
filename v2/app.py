import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib
import json
from scipy.spatial import cKDTree
import plotly.graph_objects as go

# ── 頁面配置 ──────────────────────────────────────────────
st.set_page_config(page_title="SOLIDWIZARD | 3D 列印報價系統", layout="wide")

st.markdown("""
<style>
/* ── 全域 ── */
.stApp, .stApp > div, section[data-testid="stMain"] { background-color: #0d1117 !important; color: #FFFFFF; }
#MainMenu, footer, header { visibility: hidden; }
* { font-family: 'Segoe UI', system-ui, sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d !important; }
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }

/* ── Buttons ── */
.stButton > button { width: 100%; border-radius: 6px; font-weight: 600; background-color: #161b22 !important; border: 1px solid #30363d !important; color: #8B949E !important; height: 36px; font-size: 12px; transition: all .15s; }
.stButton > button:hover { background-color: #00C853 !important; color: #000000 !important; border-color: #00C853 !important; }

/* ── PreForm 報價卡 ── */
.price-container { background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 16px; }
.price-header { font-size: 11px; color: #8B949E; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
.price-result { color: #00C853; font-size: 36px; font-weight: 800; display: inline-block; margin-bottom: 12px; }
.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
.data-item { border-left: 3px solid #30363d; padding-left: 10px; }
.data-label { color: #8B949E; font-size: 10px; font-weight: bold; text-transform: uppercase; }
.data-value { color: #FFFFFF; font-size: 14px; font-weight: 700; }
.cost-breakdown { background: #0d1117; border-radius: 6px; padding: 12px 16px; margin-top: 12px; border: 1px solid #30363d; }
.cost-row { display: flex; justify-content: space-between; font-size: 12px; color: #8B949E; padding: 4px 0; }
.cost-row.total { font-weight: 700; color: #00C853; border-top: 1px solid #30363d; margin-top: 6px; padding-top: 8px; font-size: 13px; }
.priority-note { background: rgba(0,200,83,0.08); color: #00C853; border-left: 3px solid #00C853; padding: 8px 12px; font-size: 12px; border-radius: 0 6px 6px 0; margin-bottom: 10px; }
h4 { font-size: 12px !important; margin: 6px 0 8px !important; color: #8B949E !important; }
hr { border-color: #30363d !important; }
.model-info-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px 12px; margin-top: 8px; font-size: 11px; color: #8B949E; line-height: 2; }
.model-info-card b { color: #FFFFFF; }
div[data-testid="column"]:nth-child(2) .stButton button { background: transparent !important; border-color: transparent !important; cursor: default !important; }

/* ── 熱力圖頁首 ── */
.top-bar { display: flex; align-items: center; justify-content: space-between; padding: 10px 0 6px 0; border-bottom: 1px solid #21262d; margin-bottom: 12px; }
.top-bar-left { display: flex; align-items: center; gap: 12px; }
.logo { color: #FFFFFF; font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }
.logo span { color: #00C853; }
.subtitle { color: #8B949E; font-size: 12px; }

/* ── KPI 卡片 ── */
.kpi-row { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.kpi-card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 12px 16px; flex: 1; min-width: 120px; }
.kpi-label { color: #8B949E; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.kpi-value { color: #FFFFFF; font-size: 20px; font-weight: 800; }
.kpi-change { font-size: 11px; margin-top: 2px; }
.up   { color: #00C853; }
.down { color: #FF5252; }
.flat { color: #8B949E; }

/* ── 圖例列 ── */
.legend-row { display: flex; align-items: center; gap: 16px; margin-bottom: 8px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #8B949E; }
.legend-dot { width: 10px; height: 10px; border-radius: 2px; }

/* ── 報價區 ── */
.quote-panel { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 20px; margin-top: 12px; }
.quote-title { color: #8B949E; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.quote-price { color: #00C853; font-size: 40px; font-weight: 900; margin-bottom: 4px; }
.quote-sub { color: #8B949E; font-size: 12px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; }
.detail-cell { border-left: 2px solid #21262d; padding-left: 10px; }
.detail-label { color: #8B949E; font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
.detail-value { color: #FFFFFF; font-size: 13px; font-weight: 700; }

/* ── Streamlit 元件深色化 ── */
.stSelectbox > div > div, .stNumberInput input { background: #161b22 !important; color: #FFFFFF !important; border: 1px solid #21262d !important; border-radius: 6px !important; }
label, .stSelectbox label { color: #8B949E !important; font-size: 11px !important; }
.stDivider { border-color: #21262d !important; }
.stAlert { background: #161b22 !important; border: 1px solid #21262d !important; }
.stPlotlyChart { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── 核心狀態初始化 ──────────────────────────────────────
for k, v in [('offset', [0.0, 0.0]), ('mesh', None), ('mesh_hash', ""), ('thin_faces', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 材料資料庫（PreForm 報價用）──────────────────────────
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

# ── 材料資料庫（熱力圖用）────────────────────────────────
MATERIALS = [
    ("Clear Resin V4",       "Standard",    6900,  1.17, "透明/通用",     "#004D40"),
    ("Grey Resin V4",        "Standard",    6900,  1.17, "灰色/通用",     "#004D40"),
    ("White Resin V4",       "Standard",    6900,  1.17, "白色/通用",     "#004D40"),
    ("Black Resin V4",       "Standard",    6900,  1.17, "黑色/通用",     "#004D40"),
    ("Draft Resin V2",       "Standard",    6900,  1.10, "快速成型",      "#004D40"),
    ("Model Resin V3",       "Standard",    6900,  1.15, "精細模型",      "#004D40"),
    ("Tough 2000 Resin",     "Engineering", 8500,  1.20, "韌性/高強度",   "#1565C0"),
    ("Tough 1500 Resin",     "Engineering", 8500,  1.15, "韌性/彈性",     "#1565C0"),
    ("Durable Resin",        "Engineering", 8500,  1.15, "耐磨/彈性",     "#1565C0"),
    ("Grey Pro Resin",       "Engineering", 8500,  1.19, "工程灰/精準",   "#1565C0"),
    ("Rigid 10K Resin",      "Engineering", 12000, 1.55, "超剛性/玻纖",   "#0D47A1"),
    ("Rigid 4000 Resin",     "Engineering", 8500,  1.30, "剛性/玻纖",     "#1565C0"),
    ("Flexible 80A Resin",   "Flexible",    9500,  1.13, "Shore 80A",    "#1B5E20"),
    ("Elastic 50A Resin",    "Flexible",    9500,  1.10, "Shore 50A",    "#1B5E20"),
    ("High Temp Resin",      "Specialty",   11000, 1.25, "耐高溫 289°C",  "#E65100"),
    ("Flame Retardant",      "Specialty",   12000, 1.30, "阻燃 UL94-V0", "#B71C1C"),
    ("ESD Resin",            "Specialty",   12000, 1.22, "防靜電",        "#4A148C"),
    ("BioMed Clear",         "BioMed",      13500, 1.17, "生醫透明",      "#006064"),
    ("BioMed Amber",         "BioMed",      13500, 1.17, "生醫琥珀",      "#006064"),
    ("BioMed White",         "BioMed",      13500, 1.18, "生醫白色",      "#006064"),
    ("BioMed Black",         "BioMed",      13500, 1.18, "生醫黑色",      "#006064"),
    ("Castable Wax 40",      "Castable",    15000, 1.00, "失蠟鑄造",      "#F57F17"),
    ("Castable Wax",         "Castable",    15000, 1.00, "失蠟鑄造",      "#F57F17"),
    ("Silicone 40A",         "Specialty",   18000, 1.12, "矽膠 Shore 40A","#880E4F"),
    ("Alumina 4N Resin",     "Specialty",   25000, 2.40, "氧化鋁陶瓷",    "#37474F"),
]
df_hm = pd.DataFrame(MATERIALS, columns=["name","category","price","density","spec","color"])
df_hm["price_mL"] = df_hm["price"] / 1000

def price_color(p):
    if p <= 6900:  return "#004D40"
    if p <= 8500:  return "#1565C0"
    if p <= 10000: return "#1B5E20"
    if p <= 13000: return "#E65100"
    if p <= 16000: return "#B71C1C"
    return "#FF5252"

df_hm["map_color"] = df_hm["price"].apply(price_color)

# ── 列印機規格 ────────────────────────────────────────────
PRINTERS = {
    "Form 4":  {"w": 200.0, "d": 125.0, "h": 210.0, "layer_time_sec": 5.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0, "layer_time_sec": 6.0},
}

# ── Three.js 幾何 JSON 產生器 ──────────────────────────────
def mesh_to_threejs_json(mesh, printer_box, qty, off_x, off_y, thin_faces=None):
    W = printer_box['w']
    D = printer_box['d']
    H = printer_box['h']
    cols = max(1, int(np.ceil(np.sqrt(qty))))
    rows = max(1, int(np.ceil(qty / cols)))
    sx = mesh.extents[0] * 1.15
    sy = mesh.extents[1] * 1.15
    all_positions = []
    all_colors = []
    thin_set = set(thin_faces) if thin_faces else set()

    for i in range(qty):
        m = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols - 1) / 2.0) * sx + off_x
        ty = (r - (rows - 1) / 2.0) * sy + off_y
        tz = -m.bounds[0][2]
        m.apply_translation([tx, ty, tz])
        verts = m.vertices
        faces = m.faces
        for fi, face in enumerate(faces):
            for vi in face:
                v = verts[vi]
                all_positions.extend([float(v[0]), float(v[2]), float(-v[1])])
                if fi in thin_set:
                    all_colors.extend([1.0, 0.18, 0.18])
                else:
                    all_colors.extend([0.0, 0.506, 1.0])

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

# ── Three.js PreForm 渲染器 ────────────────────────────────
def preform_viewer_html(geo_json: dict) -> str:
    data_str = json.dumps(geo_json)
    is_over = geo_json["is_over"]
    thin_count = geo_json.get("thin_count", 0)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#1a2235; font-family:'Segoe UI',system-ui,sans-serif; overflow:hidden; }}
#wrap {{ position:relative; width:100%; height:580px; }}
canvas {{ display:block; width:100%!important; height:100%!important; touch-action:none; }}
#viewbar {{
  position:absolute; top:8px; left:50%; transform:translateX(-50%);
  display:flex; gap:3px; background:rgba(10,18,35,0.92);
  border:1px solid #2d3f5a; border-radius:6px; padding:4px 6px;
  backdrop-filter:blur(6px); z-index:10; white-space:nowrap;
  max-width:calc(100% - 16px); overflow-x:auto;
}}
.vbtn {{
  background:transparent; border:1px solid transparent;
  color:#7a9cc0; font-size:clamp(10px,2.5vw,12px); font-weight:600;
  padding:4px 8px; border-radius:4px; cursor:pointer; transition:all .15s;
  min-height:28px; touch-action:manipulation;
}}
.vbtn:hover  {{ background:#1e3a6e; color:#fff; border-color:#3b82f6; }}
.vbtn.active {{ background:#0081FF; color:#fff; border-color:#0081FF; }}
.sep {{ width:1px; background:#2d3f5a; margin:2px 2px; flex-shrink:0; }}
#info {{
  position:absolute; top:8px; left:8px;
  background:rgba(10,18,35,0.88); border:1px solid #1e3a5f;
  border-radius:6px; padding:7px 10px; font-size:clamp(10px,2.5vw,12px);
  color:#7dd3fc; line-height:1.8; pointer-events:none;
  backdrop-filter:blur(4px);
}}
#info .lbl {{
  color:#3d5a7a; font-size:clamp(9px,2vw,10px);
  text-transform:uppercase; letter-spacing:.06em;
}}
#hint {{
  position:absolute; bottom:8px; right:10px;
  font-size:clamp(9px,2vw,11px); color:#3d5a7a; line-height:1.8;
  text-align:right; pointer-events:none;
}}
#hint b {{ color:#6b8fb5; }}
@media (max-width: 500px) {{ #hint {{ display:none; }} }}
#over-badge {{
  display:none; position:absolute; bottom:8px; left:50%; transform:translateX(-50%);
  background:rgba(220,38,38,0.15); border:1px solid #f87171; border-radius:5px;
  color:#fca5a5; font-size:clamp(10px,2.5vw,12px); font-weight:700;
  padding:5px 14px; white-space:nowrap;
}}
#thin-badge {{
  display:none; position:absolute; bottom:40px; left:50%; transform:translateX(-50%);
  background:rgba(234,88,12,0.15); border:1px solid #fb923c; border-radius:5px;
  color:#fdba74; font-size:clamp(10px,2.5vw,12px); font-weight:600;
  padding:4px 12px; white-space:nowrap;
}}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c"></canvas>
  <div id="viewbar">
    <button class="vbtn" onclick="resetView()" title="重置 (F)">⌂</button>
    <div class="sep"></div>
    <button class="vbtn" id="b-iso"   onclick="setView('iso')">等角</button>
    <button class="vbtn" id="b-top"   onclick="setView('top')">俯</button>
    <button class="vbtn" id="b-front" onclick="setView('front')">前</button>
    <button class="vbtn" id="b-right" onclick="setView('right')">右</button>
    <div class="sep"></div>
    <button class="vbtn" id="b-wire"  onclick="toggleWire()">線框</button>
    <button class="vbtn" onclick="fitAll()">Fit</button>
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
const GEO = {data_str};
const W = GEO.printer.w;
const D = GEO.printer.d;
const H = GEO.printer.h;
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({{ canvas, antialias:true }});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111827);
const camera = new THREE.PerspectiveCamera(32, 1, 0.5, 100000);
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
const hw = W / 2, hd = D / 2;
const isOver = GEO.is_over;
const boxHex = isOver ? 0xe11d48 : 0x4b6a8a;
const boxMat = new THREE.LineBasicMaterial({{ color: boxHex }});
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
const gridMat = new THREE.LineBasicMaterial({{ color:0x1e3a55, transparent:true, opacity:0.9 }});
const gridMajMat = new THREE.LineBasicMaterial({{ color:0x2a5a80, transparent:true, opacity:0.7 }});
function makeGrid() {{
  const rawStep = Math.max(W, D) / 12;
  const step = Math.ceil(rawStep / 5) * 5;
  for(let x = -hw; x <= hw + 0.01; x += step) {{
    const xc = Math.round(x / step) * step;
    if(xc < -hw || xc > hw) continue;
    const isMaj = Math.abs(xc % (step * 2)) < 0.01;
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(xc, 0, -hd), new THREE.Vector3(xc, 0,  hd)
    ]);
    scene.add(new THREE.Line(g, isMaj ? gridMajMat : gridMat));
  }}
  for(let z = -hd; z <= hd + 0.01; z += step) {{
    const zc = Math.round(z / step) * step;
    if(zc < -hd || zc > hd) continue;
    const isMaj = Math.abs(zc % (step * 2)) < 0.01;
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-hw, 0, zc), new THREE.Vector3( hw, 0, zc)
    ]);
    scene.add(new THREE.Line(g, isMaj ? gridMajMat : gridMat));
  }}
  const floorGeo = new THREE.PlaneGeometry(W, D);
  const floorMat = new THREE.MeshStandardMaterial({{
    color: 0x0a1628, transparent:true, opacity:0.70, roughness:1, metalness:0, depthWrite:false
  }});
  const floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;
  floorMesh.position.y = 0.01;
  floorMesh.receiveShadow = true;
  scene.add(floorMesh);
}}
makeGrid();
let partMesh = null, wireMesh = null;
let wireOn = false;
function buildPart() {{
  if(partMesh) scene.remove(partMesh);
  if(wireMesh) scene.remove(wireMesh);
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
if(isOver) document.getElementById('over-badge').style.display = 'block';
if(GEO.thin_count > 0) document.getElementById('thin-badge').style.display = 'block';
document.getElementById('i-printer').textContent = W + ' × ' + D + ' × ' + H + ' mm';
document.getElementById('i-vol').textContent = (GEO.positions.length / 9).toLocaleString() + ' faces';
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
  const diag = Math.sqrt(W*W + D*D + H*H);
  const fovRad = camera.fov * Math.PI / 180;
  return (diag / 2) / Math.sin(fovRad / 2) * 1.45;
}}
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
    case 'iso':   sph.set(R, Math.PI/2 - Math.atan(1/Math.sqrt(2)), -Math.PI/4); break;
    case 'top':   sph.set(R, 0.001, 0); break;
    case 'front': sph.set(R, Math.PI/2, 0); break;
    case 'right': sph.set(R, Math.PI/2, -Math.PI/2); break;
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
resetView();
let dragging = false, shiftDown = false, lastX = 0, lastY = 0;
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('mousedown', e => {{
  if(e.button === 2) {{ dragging = true; shiftDown = e.shiftKey; lastX = e.clientX; lastY = e.clientY; }}
}});
window.addEventListener('mouseup', () => {{ dragging = false; }});
window.addEventListener('mousemove', e => {{
  if(!dragging) return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX; lastY = e.clientY;
  if(shiftDown || e.shiftKey) {{
    const speed = sph.radius * 0.0012;
    const right = new THREE.Vector3();
    right.crossVectors(camera.getWorldDirection(new THREE.Vector3()), camera.up).normalize();
    panOff.addScaledVector(right, -dx * speed);
    panOff.addScaledVector(camera.up, dy * speed);
  }} else {{
    sph.theta += dx * 0.007;
    sph.phi   -= dy * 0.007;
    sph.phi = Math.max(0.02, Math.min(Math.PI - 0.02, sph.phi));
  }}
  updateCam();
}});
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  sph.radius *= e.deltaY > 0 ? 1.10 : 0.91;
  sph.radius = Math.max(10, Math.min(sph.radius, 200000));
  updateCam();
}}, {{ passive:false }});
let touches = {{}};
let lastPinchDist = 0;
let lastTouchX = 0, lastTouchY = 0;
let lastMidX = 0, lastMidY = 0;
canvas.addEventListener('touchstart', e => {{
  e.preventDefault();
  for(const t of e.changedTouches) touches[t.identifier] = t;
  const pts = Object.values(touches);
  if(pts.length === 1) {{ lastTouchX = pts[0].clientX; lastTouchY = pts[0].clientY; }}
  else if(pts.length === 2) {{
    lastPinchDist = Math.hypot(pts[1].clientX - pts[0].clientX, pts[1].clientY - pts[0].clientY);
    lastMidX = (pts[0].clientX + pts[1].clientX) / 2;
    lastMidY = (pts[0].clientY + pts[1].clientY) / 2;
  }}
}}, {{ passive:false }});
canvas.addEventListener('touchmove', e => {{
  e.preventDefault();
  for(const t of e.changedTouches) touches[t.identifier] = t;
  const pts = Object.values(touches);
  if(pts.length === 1) {{
    const dx = pts[0].clientX - lastTouchX;
    const dy = pts[0].clientY - lastTouchY;
    lastTouchX = pts[0].clientX; lastTouchY = pts[0].clientY;
    sph.theta += dx * 0.007;
    sph.phi   -= dy * 0.007;
    sph.phi = Math.max(0.02, Math.min(Math.PI - 0.02, sph.phi));
    updateCam();
  }} else if(pts.length === 2) {{
    const dist = Math.hypot(pts[1].clientX - pts[0].clientX, pts[1].clientY - pts[0].clientY);
    if(lastPinchDist > 0) {{
      const factor = lastPinchDist / dist;
      sph.radius = Math.max(10, Math.min(sph.radius * factor, 200000));
    }}
    lastPinchDist = dist;
    const midX = (pts[0].clientX + pts[1].clientX) / 2;
    const midY = (pts[0].clientY + pts[1].clientY) / 2;
    const dx = midX - lastMidX;
    const dy = midY - lastMidY;
    lastMidX = midX; lastMidY = midY;
    const speed = sph.radius * 0.0012;
    const right = new THREE.Vector3();
    right.crossVectors(camera.getWorldDirection(new THREE.Vector3()), camera.up).normalize();
    panOff.addScaledVector(right, -dx * speed);
    panOff.addScaledVector(camera.up, dy * speed);
    updateCam();
  }}
}}, {{ passive:false }});
canvas.addEventListener('touchend', e => {{
  for(const t of e.changedTouches) delete touches[t.identifier];
  lastPinchDist = 0;
}}, {{ passive:false }});
window.addEventListener('keydown', e => {{
  const k = e.key.toLowerCase();
  if(k === 'f') resetView();
  if(k === 't') setView('top');
  if(k === 'r') setView('right');
  if(k === 'i') setView('iso');
}});
function onResize() {{
  const w = canvas.parentElement.clientWidth;
  const h = canvas.parentElement.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}}
window.addEventListener('resize', onResize);
onResize();
(function loop() {{
  requestAnimationFrame(loop);
  renderer.render(scene, camera);
}})();
</script>
</body>
</html>"""


# ════════════════════════════════════════════════════════════
#  側邊欄（PreForm 報價設定）
# ════════════════════════════════════════════════════════════
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
    support_ratio = st.slider("支撐結構體積係數 (%)", 0, 50, 20, 5)
    layer_thickness = st.selectbox("層厚 (mm)", [0.05, 0.1, 0.2], index=1)
    min_t_val = st.slider("薄度偵測閾值 (mm)", 0.0, 5.0, 0.5, 0.5)
    handling_fee = st.number_input("基本處理費 / 件 (NT$)", min_value=0, value=200, step=50)


# ════════════════════════════════════════════════════════════
#  主畫面：兩個 Tab
# ════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["⚙️ PreForm 模擬報價", "📊 材料熱力圖"])

# ────────────────────────────────────────────────────────────
#  Tab 1：PreForm 模擬報價
# ────────────────────────────────────────────────────────────
with tab1:
    u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
    printer_spec = PRINTERS[p_choice]

    if up_file:
        file_bytes = up_file.read()
        file_hash = hashlib.md5(file_bytes).hexdigest()
        if st.session_state.mesh_hash != file_hash:
            load_error = None
            raw = None
            try:
                loaded = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
                if isinstance(loaded, trimesh.Scene):
                    meshes = [g for g in loaded.geometry.values()
                              if isinstance(g, trimesh.Trimesh) and len(g.faces) > 0]
                    if not meshes:
                        raise ValueError("STL 內沒有有效的 mesh 物件")
                    raw = trimesh.util.concatenate(meshes)
                elif isinstance(loaded, trimesh.Trimesh):
                    raw = loaded
                else:
                    raise ValueError(f"不支援的物件類型：{type(loaded)}")
                if len(raw.faces) == 0:
                    raise ValueError("模型沒有任何面（可能是空的 STL）")
                if np.any(np.isnan(raw.vertices)) or np.any(np.isinf(raw.vertices)):
                    raise ValueError("模型頂點含有 NaN 或 Inf，檔案可能損毀")
                raw.fix_normals()
                trimesh.repair.fill_holes(raw)
                trimesh.repair.fix_winding(raw)
                try:
                    if raw.volume < 0:
                        raw.invert()
                except Exception:
                    pass
                if np.any(raw.extents < 1e-6):
                    raise ValueError(f"模型尺寸過小或為零（extents: {raw.extents}），請確認單位是否正確（應為 mm）")
                raw.apply_translation(-raw.bounds[0])
                raw.apply_translation([-raw.extents[0] / 2, -raw.extents[1] / 2, 0])
            except Exception as e:
                load_error = str(e)
                raw = None

            if load_error:
                st.error(f"❌ 無法載入此 STL 檔案：{load_error}")
                st.info("💡 建議：用 Meshmixer 或 PrusaSlicer 的「修復」功能先處理此檔案，再重新上傳。")
                st.session_state.mesh = None
                st.session_state.mesh_hash = ""
            else:
                st.session_state.mesh = raw
                st.session_state.mesh_hash = file_hash
                st.session_state.offset = [0.0, 0.0]
                st.session_state.thin_faces = None

    use_stl = up_file and st.session_state.mesh is not None
    use_manual = not use_stl and manual_v > 0

    if use_stl or use_manual:
        if use_stl:
            try:
                vol = st.session_state.mesh.volume
                if not np.isfinite(vol) or vol <= 0:
                    vol = st.session_state.mesh.convex_hull.volume
                    st.caption("⚠️ 模型非封閉（非 watertight），體積以凸包近似計算。")
            except Exception:
                vol = st.session_state.mesh.convex_hull.volume
                st.caption("⚠️ 體積計算失敗，以凸包近似。")
            model_vol = abs(vol)
        else:
            model_vol = manual_v if m_unit == "mm³" else manual_v * 1000

        support_vol = model_vol * (support_ratio / 100)
        total_vol_per_unit = model_vol + support_vol
        material_cost_total = total_vol_per_unit * u_cost * qty
        handling_total = handling_fee * qty
        subtotal = material_cost_total + handling_total
        final_price = subtotal * markup
        mat_price_per_liter = df_m.loc[df_m["材料名稱"] == m_choice, "單價"].values[0]
        model_h = st.session_state.mesh.extents[2] if use_stl else model_vol ** (1 / 3)
        n_layers = int(np.ceil(model_h / layer_thickness))
        print_time = (n_layers * printer_spec["layer_time_sec"]) / 60

        st.markdown(f"""
        <div class="price-container">
            <div style="font-size:13px;color:#64748b;font-weight:bold;margin-bottom:4px;">PREFORM 預估總列印成本</div>
            <div class="price-result">NT$ {final_price:,.0f}</div>
            <div class="data-grid">
                <div class="data-item"><div class="data-label">模型體積</div><div class="data-value">{model_vol:,.1f} mm³</div></div>
                <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
                <div class="data-item"><div class="data-label">含支撐消耗 (mL)</div><div class="data-value">{total_vol_per_unit * qty / 1000:,.2f} mL</div></div>
                <div class="data-item"><div class="data-label">列印機型</div><div class="data-value">{p_choice}</div></div>
                <div class="data-item"><div class="data-label">預估列印時間</div><div class="data-value">≈ {print_time:.0f} 分鐘</div></div>
                <div class="data-item"><div class="data-label">層數（{layer_thickness}mm）</div><div class="data-value">{n_layers:,} 層</div></div>
                <div class="data-item"><div class="data-label">材料單價</div><div class="data-value">NT$ {mat_price_per_liter:,} / L</div></div>
                <div class="data-item"><div class="data-label">材料單價換算</div><div class="data-value">NT$ {mat_price_per_liter/1000:.2f} / mL</div></div>
            </div>
            <div class="cost-breakdown">
                <div class="cost-row">
                    <span>材料費（含支撐 {support_ratio}%，{total_vol_per_unit / 1000:.2f} mL/件 × NT${mat_price_per_liter/1000:.2f}/mL）× {qty} 件</span>
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

        if use_stl:
            st.divider()
            col_tool, col_view = st.columns([1, 3])

            with col_tool:
                st.markdown("#### 🎯 擺放優化")

                if st.button("⚡ 最佳列印位置", use_container_width=True):
                    with st.spinner("正在計算最佳方向..."):
                        mesh_orig = st.session_state.mesh.copy()

                        def fibonacci_directions(n=120):
                            indices = np.arange(n)
                            phi = np.pi * (3 - np.sqrt(5))
                            y = 1 - (indices / (n - 1)) * 2
                            radius = np.sqrt(1 - y * y)
                            theta = phi * indices
                            x = np.cos(theta) * radius
                            z = np.sin(theta) * radius
                            dirs = np.column_stack([x, y, z])
                            return dirs[dirs[:, 2] >= -0.1]

                        directions = fibonacci_directions(160)
                        face_areas = mesh_orig.area_faces
                        face_normals = mesh_orig.face_normals
                        total_area = mesh_orig.area
                        best_score = np.inf
                        best_rot = None
                        best_meta = {}

                        for up_dir in directions:
                            up_dir = up_dir / np.linalg.norm(up_dir)
                            z = np.array([0, 0, 1.0])
                            axis = np.cross(up_dir, z)
                            axis_len = np.linalg.norm(axis)
                            if axis_len < 1e-8:
                                if np.dot(up_dir, z) > 0:
                                    rot_mat = np.eye(4)
                                else:
                                    rot_mat = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
                            else:
                                angle = np.arctan2(axis_len, np.dot(up_dir, z))
                                rot_mat = trimesh.transformations.rotation_matrix(angle, axis / axis_len)
                            rot3 = rot_mat[:3, :3]
                            rotated_normals = face_normals @ rot3.T
                            down_mask = rotated_normals[:, 2] < -0.707
                            support_area = np.sum(face_areas[down_mask])
                            score_support = support_area / total_area
                            rotated_verts = (mesh_orig.vertices @ rot3.T)
                            z_min = rotated_verts[:, 2].min()
                            z_range = rotated_verts[:, 2].max() - z_min
                            bottom_mask = rotated_verts[:, 2] < z_min + z_range * 0.1
                            if bottom_mask.sum() > 0:
                                bv = rotated_verts[bottom_mask]
                                cross_area = (bv[:, 0].max() - bv[:, 0].min()) * (bv[:, 1].max() - bv[:, 1].min())
                                bbox_xy = (rotated_verts[:, 0].max() - rotated_verts[:, 0].min()) * (rotated_verts[:, 1].max() - rotated_verts[:, 1].min())
                                score_cross = cross_area / (bbox_xy + 1e-6)
                            else:
                                score_cross = 1.0
                            height = z_range
                            bbox_diag = np.sqrt(
                                (rotated_verts[:, 0].max() - rotated_verts[:, 0].min())**2 +
                                (rotated_verts[:, 1].max() - rotated_verts[:, 1].min())**2 +
                                (rotated_verts[:, 2].max() - rotated_verts[:, 2].min())**2
                            )
                            score_height = height / (bbox_diag + 1e-6)
                            score = 0.50 * score_support + 0.30 * score_cross + 0.20 * score_height
                            if score < best_score:
                                best_score = score
                                best_rot = rot_mat
                                best_meta = {"support_pct": score_support * 100, "height": height, "score": score}

                        if best_rot is not None:
                            m = st.session_state.mesh
                            m.apply_transform(best_rot)
                            m.apply_translation(-m.bounds[0])
                            m.apply_translation([-m.extents[0]/2, -m.extents[1]/2, 0])
                            st.session_state.thin_faces = None
                            st.success(f"✅ 最佳方向已套用｜支撐面積 {best_meta['support_pct']:.1f}%｜列印高度 {best_meta['height']:.1f} mm")
                            st.rerun()

                st.markdown("<div style='font-size:11px;color:#64748b;margin:6px 0 2px;font-weight:600;'>快速旋轉</div>", unsafe_allow_html=True)
                rca, rcb, rcc = st.columns(3)
                if rca.button("X 90°", use_container_width=True):
                    m = st.session_state.mesh
                    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
                    m.apply_translation(-m.bounds[0]); m.apply_translation([-m.extents[0]/2,-m.extents[1]/2,0])
                    st.session_state.thin_faces = None; st.rerun()
                if rcb.button("Y 90°", use_container_width=True):
                    m = st.session_state.mesh
                    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,1,0]))
                    m.apply_translation(-m.bounds[0]); m.apply_translation([-m.extents[0]/2,-m.extents[1]/2,0])
                    st.session_state.thin_faces = None; st.rerun()
                if rcc.button("Z 90°", use_container_width=True):
                    m = st.session_state.mesh
                    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,0,1]))
                    m.apply_translation(-m.bounds[0]); m.apply_translation([-m.extents[0]/2,-m.extents[1]/2,0])
                    st.session_state.thin_faces = None; st.rerun()

                if st.button("↩ 重置旋轉＋位置", use_container_width=True):
                    st.session_state.offset = [0.0, 0.0]
                    st.session_state.mesh_hash = ""
                    st.session_state.thin_faces = None
                    st.rerun()

                st.divider()
                st.markdown("#### 📏 位置微調")
                step_mm = st.select_slider("步距 (mm)", options=[1, 5, 10, 20], value=10)
                _, mc, _ = st.columns([1, 2, 1])
                mc.button("▲ Y+", use_container_width=True, key="y_plus",
                          on_click=lambda: st.session_state.update({"offset": [st.session_state.offset[0], st.session_state.offset[1]+step_mm]}))
                lc, _, rc = st.columns([1, 1, 1])
                lc.button("◀ X-", use_container_width=True, key="x_minus",
                          on_click=lambda: st.session_state.update({"offset": [st.session_state.offset[0]-step_mm, st.session_state.offset[1]]}))
                rc.button("▶ X+", use_container_width=True, key="x_plus",
                          on_click=lambda: st.session_state.update({"offset": [st.session_state.offset[0]+step_mm, st.session_state.offset[1]]}))
                _, mc2, _ = st.columns([1, 2, 1])
                mc2.button("▼ Y-", use_container_width=True, key="y_minus",
                           on_click=lambda: st.session_state.update({"offset": [st.session_state.offset[0], st.session_state.offset[1]-step_mm]}))
                ox, oy = st.session_state.offset
                st.markdown(f"<div style='text-align:center;font-size:11px;color:#64748b;margin-top:4px'>偏移　X: <b>{ox:+.0f}</b> mm　Y: <b>{oy:+.0f}</b> mm</div>", unsafe_allow_html=True)
                if st.button("⊙ 歸零", use_container_width=True):
                    st.session_state.offset = [0.0, 0.0]; st.rerun()

                st.divider()
                st.markdown("#### 🔍 品質檢測")
                if st.button("🔴 薄壁偵測", use_container_width=True):
                    mesh_q = st.session_state.mesh
                    tree = cKDTree(mesh_q.triangles_center)
                    thin_set = set()
                    for fi, (center, normal) in enumerate(zip(mesh_q.triangles_center, mesh_q.face_normals)):
                        dists, idxs = tree.query(center, k=6)
                        for dist, nfi in zip(dists[1:], idxs[1:]):
                            if dist < min_t_val and np.dot(normal, mesh_q.face_normals[nfi]) < -0.5:
                                thin_set.add(fi); break
                    st.session_state.thin_faces = thin_set
                    if thin_set:
                        st.warning(f"⚠️ {len(thin_set)} 個薄壁面（< {min_t_val} mm）")
                    else:
                        st.success("✅ 無薄壁問題")

                if st.button("✕ 清除標記", use_container_width=True):
                    st.session_state.thin_faces = None; st.rerun()

                m = st.session_state.mesh
                st.markdown(
                    f"""<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;
                    padding:8px 10px;margin-top:8px;font-size:11px;color:#475569;line-height:1.9'>
                    <b style='color:#0f172a'>模型資訊</b><br>
                    尺寸：{m.extents[0]:.1f} × {m.extents[1]:.1f} × {m.extents[2]:.1f} mm<br>
                    面數：{len(m.faces):,}<br>
                    封閉：{'✅ 是' if m.is_watertight else '⚠️ 否'}</div>""",
                    unsafe_allow_html=True
                )

            with col_view:
                geo_json = mesh_to_threejs_json(
                    st.session_state.mesh, printer_spec, qty,
                    st.session_state.offset[0], st.session_state.offset[1],
                    thin_faces=st.session_state.thin_faces
                )
                if geo_json["is_over"]:
                    st.error("⚠️ 零件超出設備列印範圍！請調整位置或數量。")
                html_code = preform_viewer_html(geo_json)
                st.components.v1.html(html_code, height=620, scrolling=False)
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

# ────────────────────────────────────────────────────────────
#  Tab 2：材料熱力圖
# ────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="top-bar">
      <div class="top-bar-left">
        <div class="logo">SOLID<span>WIZARD</span></div>
        <div class="subtitle">Formlabs 材料報價熱力圖 · 實威國際</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_options = ["全部材料", "Standard", "Engineering", "Flexible", "Specialty", "BioMed", "Castable"]
    selected_tab = st.radio("", tab_options, horizontal=True, label_visibility="collapsed", key="hm_tab")

    df_view = df_hm.copy() if selected_tab == "全部材料" else df_hm[df_hm["category"] == selected_tab].copy()

    avg_price = df_view["price"].mean()
    min_price = df_view["price"].min()
    max_price = df_view["price"].max()
    count     = len(df_view)

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card"><div class="kpi-label">材料數量</div><div class="kpi-value">{count}</div><div class="kpi-change flat">種 Formlabs 材料</div></div>
      <div class="kpi-card"><div class="kpi-label">平均單價</div><div class="kpi-value">NT$ {avg_price:,.0f}</div><div class="kpi-change flat">每公升</div></div>
      <div class="kpi-card"><div class="kpi-label">最低單價</div><div class="kpi-value up">NT$ {min_price:,}</div><div class="kpi-change up">↓ 最優惠</div></div>
      <div class="kpi-card"><div class="kpi-label">最高單價</div><div class="kpi-value down">NT$ {max_price:,}</div><div class="kpi-change down">↑ 特殊材料</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="legend-row">
      <div class="legend-item"><div class="legend-dot" style="background:#004D40"></div> ≤ NT$6,900</div>
      <div class="legend-item"><div class="legend-dot" style="background:#1565C0"></div> ≤ NT$8,500</div>
      <div class="legend-item"><div class="legend-dot" style="background:#1B5E20"></div> ≤ NT$10,000</div>
      <div class="legend-item"><div class="legend-dot" style="background:#E65100"></div> ≤ NT$13,000</div>
      <div class="legend-item"><div class="legend-dot" style="background:#B71C1C"></div> ≤ NT$16,000</div>
      <div class="legend-item"><div class="legend-dot" style="background:#FF5252"></div> > NT$16,000</div>
    </div>
    """, unsafe_allow_html=True)

    col_map, col_quote = st.columns([3, 1], gap="medium")

    with col_map:
        fig = go.Figure(go.Treemap(
            labels      = df_view["name"].tolist(),
            parents     = df_view["category"].tolist(),
            values      = df_view["price"].tolist(),
            customdata  = df_view[["price","price_mL","density","spec","category"]].values,
            marker=dict(
                colors = df_view["map_color"].tolist(),
                line   = dict(width=2, color="#0d1117"),
                pad    = dict(t=20, l=3, r=3, b=3),
            ),
            texttemplate = "<b>%{label}</b><br>NT$ %{value:,}",
            textfont     = dict(color="#FFFFFF", size=11),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "單價：NT$ %{customdata[0]:,} / L<br>"
                "換算：NT$ %{customdata[1]:.2f} / mL<br>"
                "密度：%{customdata[2]} g/cm³<br>"
                "特性：%{customdata[3]}<br>"
                "分類：%{customdata[4]}"
                "<extra></extra>"
            ),
            root_color   = "#0d1117",
            branchvalues = "total",
        ))
        fig.update_layout(
            paper_bgcolor = "#0d1117",
            plot_bgcolor  = "#0d1117",
            margin        = dict(t=0, l=0, r=0, b=0),
            height        = 500,
            font          = dict(color="#FFFFFF"),
        )
        selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="treemap")

    with col_quote:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        clicked_pts = (selected or {}).get("selection", {}).get("points", [])
        clicked_name = clicked_pts[0]["label"] if clicked_pts else None
        mat_names = df_view["name"].tolist()
        default_idx = mat_names.index(clicked_name) if clicked_name in mat_names else 0
        chosen = st.selectbox("選擇材料", mat_names, index=default_idx, key="hm_mat")
        row = df_view[df_view["name"] == chosen].iloc[0]
        st.markdown("---")
        vol_hm   = st.number_input("列印體積 (mm³)", min_value=0.1, value=1000.0, step=100.0, key="hm_vol")
        sup_hm   = st.slider("支撐材比例 (%)", 0, 50, 20, key="hm_sup")
        qty_hm   = st.number_input("數量", min_value=1, value=1, step=1, key="hm_qty")
        fee_hm   = st.number_input("後處理費/件 (NT$)", min_value=0, value=200, step=50, key="hm_fee")
        mark_hm  = st.number_input("加成倍率", min_value=1.0, value=2.0, step=0.1, key="hm_mark")
        total_vol_hm  = vol_hm * (1 + sup_hm / 100) * qty_hm
        mat_cost_hm   = (total_vol_hm / 1000) * row["price_mL"]
        total_cost_hm = (mat_cost_hm + fee_hm * qty_hm) * mark_hm
        badge_color = price_color(row["price"])
        st.markdown(f"""
        <div class="quote-panel">
          <div class="quote-title">⬡ 預估報價</div>
          <div class="quote-price">NT$ {total_cost_hm:,.0f}</div>
          <div class="quote-sub">{chosen}</div>
          <div class="detail-grid">
            <div class="detail-cell"><div class="detail-label">材料消耗</div><div class="detail-value">{total_vol_hm/1000:.2f} mL</div></div>
            <div class="detail-cell"><div class="detail-label">材料費</div><div class="detail-value">NT$ {mat_cost_hm*mark_hm:,.0f}</div></div>
            <div class="detail-cell"><div class="detail-label">單價</div><div class="detail-value">NT$ {row['price']:,} / L</div></div>
            <div class="detail-cell"><div class="detail-label">密度</div><div class="detail-value">{row['density']} g/cm³</div></div>
            <div class="detail-cell"><div class="detail-label">特性</div><div class="detail-value" style="font-size:11px">{row['spec']}</div></div>
            <div class="detail-cell"><div class="detail-label">分類</div><div class="detail-value" style="color:{badge_color}">{row['category']}</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
