"""
formlabs_api.py  —  Formlabs Dashboard API v0.8.1
"""
import requests, random
from datetime import datetime, timedelta

BASE      = "https://api.formlabs.com/developer/v1"
TOKEN_URL = f"{BASE}/o/token/"

# ── Auth ───────────────────────────────────────────────────────────────────────
def get_access_token(client_id: str, client_secret: str) -> dict:
    r = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id":  client_id,
        "client_secret": client_secret,
    }, timeout=15)
    r.raise_for_status()
    return r.json()

def _h(token): return {"Authorization": f"Bearer {token}"}

# ── Printers ───────────────────────────────────────────────────────────────────
def list_printers(token: str) -> list:
    r = requests.get(f"{BASE}/printers/", headers=_h(token), timeout=20)
    r.raise_for_status()
    raw = r.json()
    # API 可能回傳 list 或 {"results": [...]}
    return raw if isinstance(raw, list) else raw.get("results", raw)

def build_printer_map(printers: list) -> dict:
    """
    建立完整的對照表，key 可以是 serial 或 alias（兩種都能查到 alias）。
    從截圖可知 prints[].printer 回傳的就是 alias（如 TealMoa），
    所以必須把 alias→alias 也加進去。
    """
    m = {}
    for p in printers:
        serial = (p.get("serial") or "").strip()
        alias  = (p.get("alias")  or "").strip()
        name   = alias if alias else serial
        # serial → name
        if serial:
            m[serial] = name
            m[serial.lower()] = name
        # alias → name（讓 alias 值也能直接查到）
        if alias:
            m[alias] = name
            m[alias.lower()] = name
    return m

# ── Prints ─────────────────────────────────────────────────────────────────────
def list_prints(token, date_gt=None, date_lt=None,
                printer=None, status=None, page=1, per_page=100) -> dict:
    params = {"page": page, "per_page": per_page}
    if date_gt: params["date__gt"] = date_gt
    if date_lt: params["date__lt"] = date_lt
    if printer: params["printer"]  = printer
    if status:  params["status"]   = status
    r = requests.get(f"{BASE}/prints/", headers=_h(token), params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def list_all_prints(token, **kw) -> list:
    out, page = [], 1
    while True:
        data  = list_prints(token, page=page, per_page=100, **kw)
        batch = data.get("results", [])
        out.extend(batch)
        if not data.get("next") or not batch:
            break
        page += 1
    return out

def normalise_prints(prints: list, printer_map: dict) -> list:
    """
    為每筆列印紀錄新增：
      printer_name    — 機器顯示名稱（alias）
      material_display — 材料顯示名稱
      user_display     — 使用者顯示名稱
      success_status   — SUCCESS / FAILURE / UNKNOWN
    """
    out = []
    for p in prints:
        p = dict(p)
        # ── 機器名稱
        raw = str(p.get("printer") or "").strip()
        p["printer_name"] = (
            printer_map.get(raw)
            or printer_map.get(raw.lower())
            or raw
            or "未知"
        )
        # ── 材料
        mn = (p.get("material_name") or "").strip()
        m  = (p.get("material")      or "").strip()
        p["material_display"] = mn if mn else (m if m else "未知")
        # ── 使用者
        u  = p.get("user") or {}
        fn = (u.get("first_name") or "").strip() if isinstance(u, dict) else ""
        ln = (u.get("last_name")  or "").strip() if isinstance(u, dict) else ""
        p["user_display"] = (fn + " " + ln).strip() or "Unknown"
        # ── 成功狀態（從 print_run_success 或 status 推導）
        prs = p.get("print_run_success")
        if isinstance(prs, dict):
            p["success_status"] = prs.get("print_run_success", "UNKNOWN")
        else:
            st = p.get("status", "")
            p["success_status"] = (
                "SUCCESS" if st == "FINISHED" else
                "FAILURE" if st in ("ABORTED","ERROR") else
                "UNKNOWN"
            )
        out.append(p)
    return out

# ── Mock ───────────────────────────────────────────────────────────────────────
REAL_MACHINES = [
    {"serial":"FL-MOCK-0001","alias":"CreativeDragon", "type":"Form 3+"},
    {"serial":"FL-MOCK-0002","alias":"AluminumBowfin", "type":"Form 3L"},
    {"serial":"FL-MOCK-0003","alias":"BoldSturgeon",   "type":"Form 4"},
    {"serial":"FL-MOCK-0004","alias":"JasperGosling",  "type":"Form 4L"},
    {"serial":"FL-MOCK-0005","alias":"TealMoa",        "type":"Form 4L"},
]
MOCK_MATERIALS = [
    "Nylon 12 V1","Rigid 10K V1.1","Rigid 4000 V1","Clear V5",
    "Tough","Tough 2000 V1.1","Grey V5","White V5",
    "BioMed Clear","Castable Wax 40","Draft V2","Elastic 50A",
]
MOCK_USERS   = ["Bill Chen","Jimmy Liao","Jaylen Ho","Unknown","Admin"]
MOCK_STATUS  = ["FINISHED","FINISHED","FINISHED","ABORTED","PRINTING","PAUSED"]

def mock_printers():
    out = []
    for m in REAL_MACHINES:
        status = random.choice(["IDLE","IDLE","PRINTING"])
        mat    = random.choice(MOCK_MATERIALS)
        user   = random.choice(MOCK_USERS)
        out.append({
            "serial": m["serial"], "alias": m["alias"],
            "machine_type_id": m["type"],
            "printer_status": {
                "status": status,
                "last_pinged_at": datetime.utcnow().isoformat()+"Z",
                "material_credit": round(random.uniform(0.1,1.0),2),
                "current_temperature": round(random.uniform(20,35),1),
                "current_print_run": {
                    "name": f"part_{random.randint(1000,9999)}.form",
                    "status": status,
                    "material": mat, "material_name": mat,
                    "currently_printing_layer": random.randint(50,900),
                    "layer_count": 1000,
                    "estimated_time_remaining_ms": random.randint(600_000,7_200_000),
                    "volume_ml": round(random.uniform(5,180),1),
                    "user": {"first_name": user.split()[0],
                             "last_name": user.split()[-1] if " " in user else "",
                             "email":""},
                } if status=="PRINTING" else None,
            },
            "cartridge_status": [{"cartridge":{
                "material": mat, "display_name": mat,
                "initial_volume_ml":1000,
                "volume_dispensed_ml": round(random.uniform(100,850),1),
                "is_empty": False,
            },"cartridge_slot":"FRONT"}],
        })
    return out

def mock_prints(days=90):
    out, now = [], datetime.utcnow()
    aliases = [m["alias"] for m in REAL_MACHINES]   # mock 直接用 alias 模擬 API 回傳
    for i in range(400):
        start  = now - timedelta(days=random.randint(0,days),
                                  hours=random.randint(0,23),
                                  minutes=random.randint(0,59))
        dur    = random.randint(900_000,18_000_000)
        mat    = random.choice(MOCK_MATERIALS)
        user   = random.choice(MOCK_USERS)
        alias  = random.choice(aliases)
        st_val = random.choice(MOCK_STATUS)
        fn,*ln = user.split()
        out.append({
            "guid": f"mock-{i:04d}",
            "name": f"part_{random.randint(1000,9999)}.form",
            "printer": alias,           # 直接用 alias，模擬 Formlabs API 實際行為
            "status": st_val,
            "material": mat, "material_name": mat,
            "volume_ml": round(random.uniform(2,250),1),
            "layer_count": random.randint(50,3000),
            "layer_thickness_mm": random.choice([0.05,0.1,0.15,0.2]),
            "print_started_at": start.isoformat()+"Z",
            "print_finished_at":(start+timedelta(milliseconds=dur)).isoformat()+"Z",
            "elapsed_duration_ms": dur,
            "user":{"first_name":fn,"last_name":" ".join(ln),"email":f"{fn}@example.com"},
            "print_run_success":{"print_run_success":(
                "SUCCESS" if st_val=="FINISHED" else
                "FAILURE" if st_val=="ABORTED" else "UNKNOWN"
            )},
        })
    return out
