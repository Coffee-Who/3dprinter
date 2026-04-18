"""
formlabs_api.py
Wrapper around the Formlabs Dashboard Developer API v0.8.1
Docs: https://formlabs-dashboard-api-resources.s3.amazonaws.com/formlabs-web-api-latest.html
"""

import requests
import streamlit as st
from datetime import datetime, timedelta, timezone

BASE = "https://api.formlabs.com/developer/v1"
TOKEN_URL = f"{BASE}/o/token/"
REVOKE_URL = f"{BASE}/o/revoke_token/"

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token(client_id: str, client_secret: str) -> dict:
    """Exchange client credentials for an access token."""
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()          # {"access_token":..., "expires_in":86400, ...}


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ── Printers ──────────────────────────────────────────────────────────────────

def list_printers(token: str) -> list:
    resp = requests.get(f"{BASE}/printers/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()          # list of printer objects


def get_printer(token: str, serial: str) -> dict:
    resp = requests.get(f"{BASE}/printers/{serial}/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Prints ────────────────────────────────────────────────────────────────────

def list_prints(token: str,
                date_gt: str = None,
                date_lt: str = None,
                printer: str = None,
                status: str = None,
                material: str = None,
                page: int = 1,
                per_page: int = 100) -> dict:
    """
    Returns paginated print list.
    date_gt / date_lt: ISO 8601 strings e.g. '2024-01-01T00:00:00Z'
    """
    params = {"page": page, "per_page": per_page}
    if date_gt:   params["date__gt"] = date_gt
    if date_lt:   params["date__lt"] = date_lt
    if printer:   params["printer"]  = printer
    if status:    params["status"]   = status
    if material:  params["material"] = material

    resp = requests.get(f"{BASE}/prints/", headers=_headers(token),
                        params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()          # {"count":..., "results":[...]}


def list_all_prints(token: str, **kwargs) -> list:
    """Auto-paginate and return all matching prints."""
    results = []
    page = 1
    while True:
        data = list_prints(token, page=page, per_page=100, **kwargs)
        results.extend(data.get("results", []))
        if not data.get("next"):
            break
        page += 1
    return results


# ── Cartridges / Tanks ────────────────────────────────────────────────────────

def list_cartridges(token: str) -> list:
    resp = requests.get(f"{BASE}/cartridges/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()


def list_tanks(token: str) -> list:
    resp = requests.get(f"{BASE}/tanks/", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Events ────────────────────────────────────────────────────────────────────

def list_events(token: str, page: int = 1, per_page: int = 100) -> dict:
    resp = requests.get(f"{BASE}/events/",
                        headers=_headers(token),
                        params={"page": page, "per_page": per_page},
                        timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Demo / Mock data (used when no API key is supplied) ───────────────────────

import random
from datetime import datetime, timedelta

MOCK_MATERIALS = [
    "Tough 1500 Resin V2", "Grey Resin V5", "Clear Resin V5",
    "Rigid 10K Resin", "BioMed Clear Resin", "Castable Wax 40",
    "Nylon 12 Powder", "Elastic 50A Resin",
]
MOCK_USERS = ["陳工程師", "林業務", "王技術", "張應用", "Demo User"]
MOCK_MACHINES = ["Form 4 #001", "Form 4 #002", "Form 4L #001",
                 "Form 4B #001", "Fuse 1+ #001"]
MOCK_STATUSES = ["FINISHED", "FINISHED", "FINISHED", "ABORTED", "PRINTING", "PAUSED"]


def mock_printers() -> list:
    printers = []
    for i, name in enumerate(MOCK_MACHINES):
        status = random.choice(["IDLE", "PRINTING", "IDLE", "PRINTING"])
        printers.append({
            "serial": f"FL-MOCK-{i+1:03d}",
            "alias": name,
            "machine_type_id": "form-4" if "Form 4" in name else "fuse-1",
            "printer_status": {
                "status": status,
                "last_pinged_at": datetime.utcnow().isoformat() + "Z",
                "material_credit": round(random.uniform(0.2, 1.0), 2),
                "current_temperature": round(random.uniform(20, 35), 1),
                "current_print_run": {
                    "name": f"sample_part_{random.randint(100,999)}.form",
                    "status": status,
                    "material": random.choice(MOCK_MATERIALS),
                    "material_name": random.choice(MOCK_MATERIALS),
                    "currently_printing_layer": random.randint(0, 800),
                    "layer_count": 1000,
                    "estimated_time_remaining_ms": random.randint(0, 7200000),
                    "volume_ml": round(random.uniform(5, 180), 1),
                    "user": {"first_name": random.choice(MOCK_USERS), "last_name": "", "email": ""},
                } if status == "PRINTING" else None,
            },
            "cartridge_status": [{
                "cartridge": {
                    "material": random.choice(MOCK_MATERIALS),
                    "display_name": random.choice(MOCK_MATERIALS),
                    "initial_volume_ml": 1000,
                    "volume_dispensed_ml": round(random.uniform(100, 900), 1),
                    "is_empty": False,
                },
                "cartridge_slot": "FRONT",
            }],
        })
    return printers


def mock_prints(days: int = 30) -> list:
    prints = []
    now = datetime.utcnow()
    for i in range(180):
        start = now - timedelta(days=random.randint(0, days),
                                hours=random.randint(0, 23),
                                minutes=random.randint(0, 59))
        dur_ms = random.randint(1_800_000, 14_400_000)
        mat = random.choice(MOCK_MATERIALS)
        user_name = random.choice(MOCK_USERS)
        machine = random.choice(MOCK_MACHINES)
        st_val = random.choice(MOCK_STATUSES)
        prints.append({
            "guid": f"mock-{i:04d}",
            "name": f"part_{random.randint(1000,9999)}.form",
            "printer": machine,
            "status": st_val,
            "material": mat,
            "material_name": mat,
            "volume_ml": round(random.uniform(2, 200), 1),
            "layer_count": random.randint(50, 2000),
            "layer_thickness_mm": random.choice([0.05, 0.1, 0.15, 0.2]),
            "print_started_at": start.isoformat() + "Z",
            "print_finished_at": (start + timedelta(milliseconds=dur_ms)).isoformat() + "Z",
            "elapsed_duration_ms": dur_ms,
            "estimated_duration_ms": dur_ms + random.randint(-300000, 300000),
            "user": {
                "first_name": user_name,
                "last_name": "",
                "email": f"{user_name.lower().replace(' ','')}@example.com",
            },
            "print_run_success": {
                "print_run_success": "SUCCESS" if st_val == "FINISHED" else
                                     ("FAILURE" if st_val == "ABORTED" else "UNKNOWN"),
            },
        })
    return prints
