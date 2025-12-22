from __future__ import annotations

import json, os, re, time, hashlib, subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

HLS_DIR = Path(os.getenv("STREAM_COPILOT_HLS_DIR", "/var/www/html/hls"))
M3U8 = HLS_DIR / os.getenv("STREAM_COPILOT_HLS_M3U8", "preview.m3u8")
OUT_JSON = Path(os.getenv("STREAM_COPILOT_TRANSCRIPT_JSON", "/root/stream-copilot/data/transcript.json"))

# Whisper model options: tiny/base/small (tiny is fastest)
WHISPER_MODEL = os.getenv("STREAM_COPILOT_WHISPER_MODEL", "base")
LANG = os.getenv("STREAM_COPILOT_WHISPER_LANG", "en")

POLL_SEC = float(os.getenv("STREAM_COPILOT_TRANSCRIBE_POLL", "1.0"))
MAX_LINES = int(os.getenv("STREAM_COPILOT_TRANSCRIPT_MAX_LINES", "40"))

def _atomic_write(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)

def _read_m3u8_latest_ts(m3u8_text: str) -> Optional[str]:
    # Grab last .ts line
    lines = [ln.strip() for ln in m3u8_text.splitlines() if ln.strip() and not ln.startswith("#")]
    ts = None
    for ln in lines[::-1]:
        if ln.endswith(".ts"):
            ts = ln
            break
    return ts

def _ffmpeg_extract_wav(ts_path: Path, wav_path: Path) -> None:
    # -vn: no video, resample to 16k mono PCM s16le
    cmd = [
        "ffmpeg","-hide_banner","-loglevel","error",
        "-y","-i", str(ts_path),
        "-vn","-ac","1","-ar","16000",
        "-f","wav", str(wav_path)
    ]
    subprocess.check_call(cmd)

def _sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def _understand(lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Lightweight “active understanding”: keywords + likely intent + short summary
    text = " ".join([l.get("text","") for l in lines[-10:]]).strip().lower()
    intents = []
    if any(k in text for k in ["restart", "systemctl", "service", "nginx", "uvicorn"]):
        intents.append("ops/change")
    if any(k in text for k in ["endpoint", "api", "route", "post", "get", "json"]):
        intents.append("backend/api")
    if any(k in text for k in ["ui", "css", "card", "layout", "dashboard", "preview"]):
        intents.append("ui/polish")
    if any(k in text for k in ["obs", "scene", "websocket", "chat"]):
        intents.append("stream/integrations")
    if not intents:
        intents.append("general/build")

    # “What’s happening” one-liner
    if "ops/change" in intents:
        what = "Working on services / server config changes."
    elif "backend/api" in intents:
        what = "Building backend API wiring + state."
    elif "ui/polish" in intents:
        what = "Polishing dashboard UI and preview/overlays."
    elif "stream/integrations" in intents:
        what = "Wiring stream integrations (OBS/chat/preview)."
    else:
        what = "Building live on-stream."

    # Keywords (very cheap)
    words = re.findall(r"[a-z0-9]{4,}", text)
    stop = set(["this","that","with","from","your","have","will","just","like","then","what","okay","we're","were","dont","does","into","over","when","need"])
    freq: Dict[str,int] = {}
    for w in words:
        if w in stop: continue
        freq[w] = freq.get(w,0)+1
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:8]
    return {"what": what, "intents": intents[:3], "keywords": [k for k,_ in top]}

def main() -> None:
    from faster_whisper import WhisperModel

    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    last_ts = None
    seen_hash = None
    lines: List[Dict[str, Any]] = []
    last_written = 0.0

    tmp_wav = Path("/tmp/stream_copilot_hls.wav")

    while True:
        try:
            if not M3U8.exists():
                _atomic_write(OUT_JSON, {
                    "ok": False,
                    "status": "waiting_for_m3u8",
                    "m3u8": str(M3U8),
                    "updated": time.time(),
                    "lines": lines[-MAX_LINES:],
                    "understanding": _understand(lines),
                })
                time.sleep(POLL_SEC)
                continue

            m3 = M3U8.read_text(encoding="utf-8", errors="ignore")
            ts_name = _read_m3u8_latest_ts(m3)
            if not ts_name:
                time.sleep(POLL_SEC)
                continue

            if ts_name == last_ts and (time.time() - last_written) < 2.0:
                time.sleep(POLL_SEC)
                continue

            ts_path = HLS_DIR / ts_name
            if not ts_path.exists():
                time.sleep(POLL_SEC)
                continue

            h = _sha1(ts_path)
            if h == seen_hash:
                time.sleep(POLL_SEC)
                continue

            # Extract audio -> transcribe
            _ffmpeg_extract_wav(ts_path, tmp_wav)

            segments, info = model.transcribe(str(tmp_wav), language=LANG, vad_filter=True)
            chunk_texts = []
            chunk_conf = []

            for seg in segments:
                t = (seg.text or "").strip()
                if not t:
                    continue
                chunk_texts.append(t)
                # faster-whisper doesn't expose a perfect “confidence”; use avg logprob proxy if present
                conf = getattr(seg, "avg_logprob", None)
                if conf is None:
                    chunk_conf.append(0.55)
                else:
                    # avg_logprob ~ [-5..0], map to ~[0..1]
                    chunk_conf.append(max(0.0, min(1.0, 1.0 + (float(conf)/5.0))))

            text = " ".join(chunk_texts).strip()
            if text:
                conf = sum(chunk_conf)/len(chunk_conf) if chunk_conf else 0.55
                lines.append({
                    "ts": time.time(),
                    "text": text,
                    "confidence": round(float(conf), 3),
                    "source": "hls",
                    "segment": ts_name,
                    "model": WHISPER_MODEL,
                })
                lines = lines[-MAX_LINES:]

            payload = {
                "ok": True,
                "status": "running",
                "m3u8": str(M3U8),
                "latest_ts": ts_name,
                "updated": time.time(),
                "lines": lines[-MAX_LINES:],
                "understanding": _understand(lines),
            }
            _atomic_write(OUT_JSON, payload)

            last_ts = ts_name
            seen_hash = h
            last_written = time.time()

        except Exception as e:
            _atomic_write(OUT_JSON, {
                "ok": False,
                "status": "error",
                "error": str(e),
                "updated": time.time(),
                "lines": lines[-MAX_LINES:],
                "understanding": _understand(lines),
            })
            time.sleep(1.5)

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    main()
