"""
formlabs_api.py  —  Formlabs Dashboard API v0.8.1 wrapper
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

def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Printers ───────────────────────────────────────────────────────────────────
def list_printers(token: str) -> list:
    resp = requests.get(f"{BASE}/printers/", headers=_h(token), timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_printer_map(printers: list) -> dict:
    """
    回傳多種 key 的對照表，確保無論 prints.printer 是
    serial、alias、大小寫變體都能比對到顯示名稱。
    """
    m = {}
    for p in printers:
        serial  = (p.get("serial")  or "").strip()
        alias   = (p.get("alias")   or "").strip()
        display = alias if alias else serial

        for key in [serial, serial.lower(), serial.upper()]:
            if key:
                m[key] = display
        for key in [alias, alias.lower()]:
            if key and key not in m:
                m[key] = display
    return m


def normalise_prints(prints: list, printer_map: dict) -> list:
    """
    把每筆列印紀錄統一成 printer_name（機器顯示名稱）和 material_display。

    Formlabs API 的 prints[].printer 欄位可能是：
      1. serial number（如 "3Z19-A123"）→ 用 printer_map[serial] 換成 alias
      2. 已經是 alias（如 "TealMoa"）→ 直接使用
    兩種情況都處理。
    """
    # 建立雙向 lookup：serial→alias 和 alias→alias（讓 alias 也能查到自己）
    lookup = dict(printer_map)
    for alias in list(printer_map.values()):
        lookup[alias] = alias          # alias → alias 直通

    out = []
    for p in prints:
        p = dict(p)
        raw = str(p.get("printer") or "").strip()
        # 查 lookup，查不到就保留原始值（可能是其他帳號機器）
        p["printer_name"] = lookup.get(raw) or lookup.get(raw.lower()) or raw or "未知"

        mn = (p.get("material_name") or "").strip()
        m  = (p.get("material")      or "").strip()
        p["material_display"] = mn if mn else (m if m else "未知")

        out.append(p)
    return out



# ── Mock data ──────────────────────────────────────────────────────────────────
REAL_MACHINES = [
    {"serial": "FL-MOCK-0001", "alias": "CreativeDragon",  "type": "Form 3+"},
    {"serial": "FL-MOCK-0002", "alias": "AluminumBowfin",  "type": "Form 3L"},
    {"serial": "FL-MOCK-0003", "alias": "BoldSturgeon",    "type": "Form 4"},
    {"serial": "FL-MOCK-0004", "alias": "JasperGosling",   "type": "Form 4L"},
]

MOCK_MATERIALS = [
    "Grey Resin V5", "Clear Resin V5", "White Resin V5", "Black Resin V5",
    "Tough 1500 Resin V2", "Tough 2000 Resin", "Rigid 10K Resin",
    "High Temp Resin", "Elastic 50A Resin", "Flexible 80A Resin",
    "BioMed Clear Resin", "BioMed Amber Resin",
    "Castable Wax Resin", "Castable Wax 40 Resin",
    "Draft Resin V2", "Nylon 12 Powder", "Nylon 12 GF Powder",
]
MOCK_USERS    = ["陳工程師", "林業務", "王技術", "張應用", "李品管", "Admin"]
MOCK_STATUSES = ["FINISHED","FINISHED","FINISHED","FINISHED","ABORTED","PRINTING","PAUSED"]


def mock_printers() -> list:
    printers = []
    for m in REAL_MACHINES:
        status = random.choice(["IDLE","IDLE","PRINTING","PRINTING"])
        mat    = random.choice(MOCK_MATERIALS)
        user   = random.choice(MOCK_USERS)
        printers.append({
            "serial":          m["serial"],
            "alias":           m["alias"],
            "machine_type_id": m["type"],
            "printer_status": {
                "status":              status,
                "last_pinged_at":      datetime.utcnow().isoformat()+"Z",
                "material_credit":     round(random.uniform(0.15, 1.0), 2),
                "current_temperature": round(random.uniform(20, 35), 1),
                "current_print_run": {
                    "name":                       f"part_{random.randint(1000,9999)}.form",
                    "status":                     status,
                    "material":                   mat,
                    "material_name":              mat,
                    "currently_printing_layer":   random.randint(50, 900),
                    "layer_count":                1000,
                    "estimated_time_remaining_ms": random.randint(600_000, 7_200_000),
                    "volume_ml":                  round(random.uniform(5, 180), 1),
                    "user": {"first_name": user, "last_name": "", "email": ""},
                } if status == "PRINTING" else None,
            },
            "cartridge_status": [{
                "cartridge": {
                    "material":            mat,
                    "display_name":        mat,
                    "initial_volume_ml":   1000,
                    "volume_dispensed_ml": round(random.uniform(100, 850), 1),
                    "is_empty":            False,
                },
                "cartridge_slot": "FRONT",
            }],
        })
    return printers


def mock_prints(days=90) -> list:
    """
    Mock 的 printer 欄位用 serial（與 mock_printers 一致），
    再經 normalise_prints → printer_name = alias。
    """
    prints = []
    now    = datetime.utcnow()
    serials = [m["serial"] for m in REAL_MACHINES]

    for i in range(400):
        start  = now - timedelta(days=random.randint(0, days),
                                  hours=random.randint(0, 23),
                                  minutes=random.randint(0, 59))
        dur_ms = random.randint(900_000, 18_000_000)
        mat    = random.choice(MOCK_MATERIALS)
        user   = random.choice(MOCK_USERS)
        serial = random.choice(serials)
        st_val = random.choice(MOCK_STATUSES)

        prints.append({
            "guid":             f"mock-{i:04d}",
            "name":             f"part_{random.randint(1000,9999)}.form",
            "printer":          serial,          # serial → 後續由 normalise_prints 換名稱
            "status":           st_val,
            "material":         mat,
            "material_name":    mat,
            "volume_ml":        round(random.uniform(2, 250), 1),
            "layer_count":      random.randint(50, 3000),
            "layer_thickness_mm": random.choice([0.05, 0.1, 0.15, 0.2]),
            "print_started_at": start.isoformat()+"Z",
            "print_finished_at":(start+timedelta(milliseconds=dur_ms)).isoformat()+"Z",
            "elapsed_duration_ms": dur_ms,
            "user": {"first_name": user, "last_name": "",
                     "email": f"{user}@example.com"},
            "print_run_success": {
                "print_run_success": (
                    "SUCCESS" if st_val=="FINISHED" else
                    "FAILURE" if st_val=="ABORTED"  else "UNKNOWN"
                )
            },
        })
    return prints
