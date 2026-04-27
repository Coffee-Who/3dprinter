"""storage.py - 資料讀寫（JSON 檔案）"""
import json, os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JOBS_FILE   = DATA_DIR / "jobs.json"
CONFIG_FILE = DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "keywords":         ["Python工程師", "資料分析師"],
    "use_104":          True,
    "use_1111":         True,
    "max_pages":        3,
    "dedup":            True,
    "exclude_keywords": [],
    "salary_min":       0,
    "locations":        [],
    "schedule_hour":    9,
    "schedule_min":     0,
    "auto_export":      True,
    "keep_days":        30,
    "last_run":         "",
}

def _ensure_dir():
    DATA_DIR.mkdir(exist_ok=True)

def load_jobs() -> list:
    _ensure_dir()
    if not JOBS_FILE.exists():
        return []
    try:
        return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_jobs(jobs: list):
    _ensure_dir()
    JOBS_FILE.write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def load_config() -> dict:
    _ensure_dir()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **cfg}
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
