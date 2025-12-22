from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(os.getenv("STREAM_COPILOT_DATA_DIR", "/root/stream-copilot/data"))
RESOURCES_FILE = DATA_DIR / "resources.json"
STREAM_FILE = DATA_DIR / "stream.json"

def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except Exception:
        return default

def _atomic_write_json(path: Path, obj) -> None:
    _ensure_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def load_resources() -> List[Dict[str, Any]]:
    return _read_json(RESOURCES_FILE, [])

def save_resources(items: List[Dict[str, Any]]) -> None:
    _atomic_write_json(RESOURCES_FILE, items)

def load_stream() -> Dict[str, Any]:
    return _read_json(STREAM_FILE, {"topic": "Untitled Stream", "mode": "default", "started": None})

def save_stream(stream: Dict[str, Any]) -> None:
    _atomic_write_json(STREAM_FILE, stream)

def new_id() -> str:
    return str(int(time.time() * 1000))
