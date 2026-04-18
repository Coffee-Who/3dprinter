"""
formlabs_api.py
Wrapper around the Formlabs Dashboard Developer API v0.8.1
"""

import requests
import random
from datetime import datetime, timedelta

BASE      = "https://api.formlabs.com/developer/v1"
TOKEN_URL = f"{BASE}/o/token/"

# ── Auth ───────────────────────────────────────────────────────────────────────
def get_access_token(client_id: str, client_secret: str) -> dict:
    resp = requests.post(TOKEN_URL, data={
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()

def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# ── Printers ───────────────────────────────────────────────────────────────────
def list_printers(token: str) -> list:
    resp = requests.get(f"{BASE}/printers/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()

def get_printer(token: str, serial: str) -> dict:
    resp = requests.get(f"{BASE}/printers/{serial}/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()

# ── Prints ─────────────────────────────────────────────────────────────────────
def list_prints(token: str, date_gt=None, date_lt=None, printer=None,
                status=None, material=None, page=1, per_page=100) -> dict:
    params = {"page": page, "per_page": per_page}
    if date_gt:  params["date__gt"] = date_gt
    if date_lt:  params["date__lt"] = date_lt
    if printer:  params["printer"]  = printer
    if status:   params["status"]   = status
    if material: params["material"] = material
    resp = requests.get(f"{BASE}/prints/", headers=_headers(token),
                        params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()

def list_all_prints(token: str, **kwargs) -> list:
    results, page = [], 1
    while True:
        data = list_prints(token, page=page, per_page=100, **kwargs)
        results.extend(data.get("results", []))
        if not data.get("next"):
            break
        page += 1
    return results

# ── Cartridges / Tanks ─────────────────────────────────────────────────────────
def list_cartridges(token: str) -> list:
    resp = requests.get(f"{BASE}/cartridges/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()

def list_tanks(token: str) -> list:
    resp = requests.get(f"{BASE}/tanks/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()

def list_events(token: str, page=1, per_page=100) -> dict:
    resp = requests.get(f"{BASE}/events/", headers=_headers(token),
                        params={"page": page, "per_page": per_page}, timeout=15)
    resp.raise_for_status()
    return resp.json()

# ── Mock / Demo data ───────────────────────────────────────────────────────────
# 真實機器清單（alias → machine type）
# ⚠️ printer 欄位用 alias 名稱，確保印表機卡片與列印紀錄完全對應
REAL_MACHINES = [
    {"alias": "CreativeDragon",  "type": "Form 3+"},
    {"alias": "AluminumBowfin",  "type": "Form 3L"},
    {"alias": "BoldSturgeon",    "type": "Form 4"},
    {"alias": "JasperGosling",   "type": "Form 4L"},
]

# 完整材料清單（涵蓋四台機器可能使用的材料）
MOCK_MATERIALS = [
    "Grey Resin V5",
    "Clear Resin V5",
    "White Resin V5",
    "Black Resin V5",
    "Tough 1500 Resin V2",
    "Tough 2000 Resin",
    "Rigid 10K Resin",
    "High Temp Resin",
    "Elastic 50A Resin",
    "Flexible 80A Resin",
    "BioMed Clear Resin",
    "BioMed Amber Resin",
    "Castable Wax Resin",
    "Castable Wax 40 Resin",
    "Draft Resin V2",
    "Color Kit - Red",
    "Nylon 12 Powder",
    "Nylon 12 GF Powder",
]

MOCK_USERS = [
    "陳工程師", "林業務", "王技術", "張應用", "李品管",
    "Demo User", "Admin",
]

MOCK_STATUSES = [
    "FINISHED", "FINISHED", "FINISHED", "FINISHED",
    "ABORTED", "PRINTING", "PAUSED",
]


def mock_printers() -> list:
    """
    回傳與 REAL_MACHINES 完全對應的模擬印表機列表。
    alias 即為 printer 欄位的值，確保卡片與紀錄一致。
    """
    printers = []
    for i, m in enumerate(REAL_MACHINES):
        status = random.choice(["IDLE", "IDLE", "PRINTING", "PRINTING"])
        mat    = random.choice(MOCK_MATERIALS)
        user   = random.choice(MOCK_USERS)

        printers.append({
            "serial":         f"FL-MOCK-{i+1:04d}",
            "alias":          m["alias"],          # ← 與 mock_prints 的 printer 欄位一致
            "machine_type_id": m["type"],
            "location":       "Taichung Office",
            "printer_status": {
                "status":               status,
                "last_pinged_at":       datetime.utcnow().isoformat() + "Z",
                "material_credit":      round(random.uniform(0.15, 1.0), 2),
                "current_temperature":  round(random.uniform(20, 35), 1),
                "current_print_run": {
                    "name":                       f"part_{random.randint(1000,9999)}.form",
                    "status":                     status,
                    "material":                   mat,
                    "material_name":              mat,   # ← 兩個欄位都填
                    "currently_printing_layer":   random.randint(50, 900),
                    "layer_count":                1000,
                    "estimated_time_remaining_ms": random.randint(600_000, 7_200_000),
                    "volume_ml":                  round(random.uniform(5, 180), 1),
                    "user": {
                        "first_name": user,
                        "last_name":  "",
                        "email":      f"{user.lower().replace(' ','')}@example.com",
                    },
                } if status == "PRINTING" else None,
            },
            "cartridge_status": [{
                "cartridge": {
                    "material":           mat,
                    "display_name":       mat,
                    "initial_volume_ml":  1000,
                    "volume_dispensed_ml": round(random.uniform(100, 850), 1),
                    "is_empty":           False,
                },
                "cartridge_slot": "FRONT",
            }],
        })
    return printers


def mock_prints(days: int = 30) -> list:
    """
    生成模擬列印紀錄。
    printer 欄位使用 REAL_MACHINES 的 alias，確保與印表機卡片名稱完全一致。
    material_name 欄位確保不為空。
    """
    prints = []
    now    = datetime.utcnow()
    # 機器名稱清單（直接從 REAL_MACHINES 取 alias）
    machine_aliases = [m["alias"] for m in REAL_MACHINES]

    for i in range(300):  # 生成 300 筆模擬資料，日期範圍覆蓋完整
        start  = now - timedelta(
            days=random.randint(0, days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        dur_ms  = random.randint(900_000, 18_000_000)
        mat     = random.choice(MOCK_MATERIALS)
        user    = random.choice(MOCK_USERS)
        machine = random.choice(machine_aliases)   # ← 直接用 alias
        st_val  = random.choice(MOCK_STATUSES)

        prints.append({
            "guid":             f"mock-{i:04d}",
            "name":             f"part_{random.randint(1000, 9999)}.form",
            "printer":          machine,           # ← 與 alias 一致
            "status":           st_val,
            "material":         mat,
            "material_name":    mat,               # ← 確保兩個欄位都有值
            "volume_ml":        round(random.uniform(2, 250), 1),
            "layer_count":      random.randint(50, 3000),
            "layer_thickness_mm": random.choice([0.05, 0.1, 0.15, 0.2]),
            "print_started_at": start.isoformat() + "Z",
            "print_finished_at": (start + timedelta(milliseconds=dur_ms)).isoformat() + "Z",
            "elapsed_duration_ms": dur_ms,
            "user": {
                "first_name": user,
                "last_name":  "",
                "email":      f"{user.lower().replace(' ','')}@example.com",
            },
            "print_run_success": {
                "print_run_success": (
                    "SUCCESS" if st_val == "FINISHED" else
                    "FAILURE" if st_val == "ABORTED"  else
                    "UNKNOWN"
                ),
            },
        })
    return prints
