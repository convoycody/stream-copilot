# Stream Co-Pilot – Server Report

Generated: **2025-12-22 19:46:59 UTC**

## System
```text
Linux localhost 6.17.0-5-generic #5-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 22 10:00:33 UTC 2025 x86_64 GNU/Linux
19:46:59 up 18:25,  4 users,  load average: 1.15, 0.90, 0.64
```

## Services

- nginx: `active`
- stream-copilot: `active`


### stream-copilot status
```text
● stream-copilot.service - Stream Co-Pilot API
     Loaded: loaded (/etc/systemd/system/stream-copilot.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-12-22 19:40:19 UTC; 6min ago
 Invocation: 23a72b2196e544e0bd22825340ee8eed
   Main PID: 296326 (uvicorn)
      Tasks: 2 (limit: 4582)
     Memory: 33M (peak: 33.5M)
        CPU: 1.037s
     CGroup: /system.slice/stream-copilot.service
             └─296326 /root/stream-copilot/venv/bin/python3 /root/stream-copilot/venv/bin/uvicorn api.app:app --host 0.0.0.0 --port 8811

Dec 22 19:40:19 localhost systemd[1]: Started stream-copilot.service - Stream Co-Pilot API.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Started server process [296326]
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Waiting for application startup.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Application startup complete.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Uvicorn running on http://0.0.0.0:8811 (Press CTRL+C to quit)
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET /favicon.ico HTTP/1.1" 404 Not Found
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET /favicon.png HTTP/1.1" 404 Not Found
Dec 22 19:41:29 localhost uvicorn[296326]: INFO:     47.231.165.111:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:42:13 localhost uvicorn[296326]: INFO:     141.51.110.126:0 - "GET / HTTP/1.1" 200 OK
```

### stream-copilot unit
```text
# /etc/systemd/system/stream-copilot.service
[Unit]
Description=Stream Co-Pilot API
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/stream-copilot
EnvironmentFile=-/root/stream-copilot/.env
ExecStart=/root/stream-copilot/venv/bin/uvicorn api.app:app --host 0.0.0.0 --port 8811
Restart=always
RestartSec=2
User=root

[Install]
WantedBy=multi-user.target
```

## Listening ports (filtered)
```text
LISTEN 0      2048         0.0.0.0:8811      0.0.0.0:*    users:(("uvicorn",pid=296326,fd=6))                                                   
LISTEN 0      511          0.0.0.0:80        0.0.0.0:*    users:(("nginx",pid=296255,fd=6),("nginx",pid=296254,fd=6),("nginx",pid=5729,fd=6))   
LISTEN 0      4096         0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=264425,fd=3),("systemd",pid=1,fd=251))                             
LISTEN 0      511          0.0.0.0:443       0.0.0.0:*    users:(("nginx",pid=296255,fd=15),("nginx",pid=296254,fd=15),("nginx",pid=5729,fd=15))
LISTEN 0      4096            [::]:22           [::]:*    users:(("sshd",pid=264425,fd=4),("systemd",pid=1,fd=252))
```

## Firewall (ufw)
```text
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 80/tcp                     ALLOW IN    Anywhere                  
[ 2] 443/tcp                    ALLOW IN    Anywhere                  
[ 3] 22/tcp                     ALLOW IN    47.231.165.111            
[ 4] 80/tcp (v6)                ALLOW IN    Anywhere (v6)             
[ 5] 443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

## Nginx proxy targets
```text
/etc/nginx/conf.d/stream-copilot.conf.bak.20251222T144402Z:6:  include /etc/nginx/snippets/stream-copilot-hls.conf;
/etc/nginx/conf.d/stream-copilot.conf.bak.20251222T144402Z:8:  # Everything else goes to the Stream Co-Pilot API/UI on :8811
/etc/nginx/conf.d/stream-copilot.conf.bak.20251222T144402Z:10:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045959Z:2:  include /etc/nginx/snippets/stream-copilot-hls.conf;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045959Z:10:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045959Z:19:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045959Z:25:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot.conf.disabled:18:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.DISABLED.20251222T051240Z:2:  include /etc/nginx/snippets/stream-copilot-hls.conf;
/etc/nginx/conf.d/stream-copilot-nocache.conf.DISABLED.20251222T051240Z:10:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.DISABLED.20251222T051240Z:19:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.DISABLED.20251222T051240Z:25:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot.conf.bak.20251222T144924Z:18:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045758Z:9:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045758Z:18:    proxy_pass http://127.0.0.1:8811;
/etc/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045758Z:24:    proxy_pass http://127.0.0.1:8811;
```

## API health

### Local
```json
{"stream":{"topic":"Untitled Stream","mode":"default","started":null},"scores":{"energy":0.65,"clarity":0.7,"engagement":0.55,"pace":0.6},"obs":{"scene":"OBS: agent mode (waiting for agent)","sources":[]},"chat":{"last_20":[]},"resources":[],"recommendations":{"talking_points":["Explain what you’re doing in one sentence.","Call out progress + what’s next.","Ask chat a specific question."],"next_question":"Do you want the quick version or the deep dive?","summary":"No chat yet."},"updated":1766432819.2955668}
```

### Public
```json
{"stream":{"topic":"Untitled Stream","mode":"default","started":null},"scores":{"energy":0.65,"clarity":0.7,"engagement":0.55,"pace":0.6},"obs":{"scene":"OBS: agent mode (waiting for agent)","sources":[]},"chat":{"last_20":[]},"resources":[],"recommendations":{"talking_points":["Explain what you’re doing in one sentence.","Call out progress + what’s next.","Ask chat a specific question."],"next_question":"Do you want the quick version or the deep dive?","summary":"No chat yet."},"updated":1766432819.435445}
```

## Repo snapshot

(not a git repo here)

## Environment (.env redacted)
```text
# ================================
# Agent mode (OBS is remote via agent)
# ================================


# Agent authentication
# Long random token – keep secret
AGENT_TOKEN=<REDACTED>

# Default agent identity (supports multi-agent later)
AGENT_DEFAULT_ID=mac-main

# LLM
LLM_PROVIDER=openai
LLM_BASE_URL=
LLM_API_KEY=

# OBS (OBS WebSocket plugin v5)
OBS_WS_URL=ws://127.0.0.1:4455
OBS_WS_PASSWORD=<REDACTED>


# Chat (start with a local websocket/aggregator)
CHAT_WS_URL=ws://127.0.0.1:8765

# App
APP_HOST=0.0.0.0
APP_PORT=8811

# Twitch chat ingest
TWITCH_CHANNEL=
TWITCH_OAUTH_TOKEN=
TWITCH_NICK=

# YouTube chat ingest
YOUTUBE_API_KEY=
YOUTUBE_LIVE_CHAT_ID=



OBS_MODE=agent
```

## Key files (first lines)

### api/app.py
```text
import time
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, Body, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from api.store import load_resources, save_resources, load_stream, save_stream
from api.ui_home import render_home
from api.ui_ipad import render_ipad_home

from collector.obs_ws import obs_worker

load_dotenv()

app = FastAPI(title="Stream Co-Pilot")

STATE = {
    "stream": {
        "topic": "Untitled Stream",
        "mode": "default",
        "started": None,
    },
    "scores": {
        "energy": 0.65,
        "clarity": 0.70,
        "engagement": 0.55,
        "pace": 0.60,
    },
    "obs": {"scene": "OBS: not connected", "sources": []},
    "chat": {"last_20": []},
    "resources": [],
    "recommendations": {
        "talking_points": [
            "Explain what you’re doing in one sentence.",
            "Call out progress + what’s next.",
            "Ask chat a specific question."
        ],
        "next_question": "Do you want the quick version or the deep dive?",
        "summary": "No chat yet."
    },
    "updated": None,
}

# ---- persistence bootstrap ----
try:
    _loaded_stream = load_stream()
except Exception:
    _loaded_stream = {"topic":"Untitled Stream","mode":"default","started":None}

try:
    _loaded_resources = load_resources()
except Exception:
    _loaded_resources = []

STATE.setdefault("stream", _loaded_stream)
STATE.setdefault("resources", _loaded_resources)
STATE.setdefault("scores", {})
STATE.setdefault("chat", {"last_20": []})
STATE.setdefault("obs", {"scene": "Unknown", "sources": []})

class ChatMsg(BaseModel):
    user: str
    text: str
    ts: float | None = None

class StreamConfig(BaseModel):
    topic: str | None = None
    mode: str | None = None

@app.on_event("startup")
async def startup_event():
    STATE["updated"] = time.time()
    asyncio.create_task(obs_worker(STATE))

@app.get("/api/state")
def get_state():
    STATE["updated"] = time.time()
    return STATE

@app.post("/api/chat")
def post_chat(msg: ChatMsg):
    m = msg.model_dump()
    if not m.get("ts"):
        m["ts"] = time.time()
    STATE["chat"]["last_20"].append(m)
    STATE["chat"]["last_20"] = STATE["chat"]["last_20"][-20:]
    STATE["recommendations"]["summary"] = f"Latest: {m['user']}: {m['text'][:80]}"
    STATE["updated"] = time.time()
    return {"ok": True}

@app.post("/api/stream/config")
def set_stream_config(cfg: StreamConfig):
    if cfg.topic:
        STATE["stream"]["topic"] = cfg.topic
    if cfg.mode:
        STATE["stream"]["mode"] = cfg.mode
    STATE["updated"] = time.time()
    return {"ok": True, "stream": STATE["stream"]}


# ---- Stream + Resources API ----
@app.get("/api/resources")
def api_get_resources():
    return {"resources": STATE.get("resources", [])}

@app.post("/api/resources")
def api_add_resource(payload: dict = Body(...)):
    """
    payload: { "text": "...", "title": optional, "url": optional, "tags": optional[list[str]] }
    """
    import time
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    item = {
        "id": str(int(time.time() * 1000)),
        "text": text,
        "title": (payload.get("title") or "").strip() or None,
        "url": (payload.get("url") or "").strip() or None,
        "tags": payload.get("tags") or [],
        "ts": time.time(),
    }

    items = list(STATE.get("resources", []))
    items.insert(0, item)
    items = items[:200]
    STATE["resources"] = items
    STATE["updated"] = time.time()
    return {"ok": True, "resource": item, "count": len(items)}

@app.delete("/api/resources/{rid}")
def api_delete_resource(rid: str):
    items = list(STATE.get("resources", []))
    new_items = [x for x in items if str(x.get("id")) != str(rid)]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="not found")
    STATE["resources"] = new_items
```

### collector/obs_ws.py
```text
import os
import asyncio
import time

def apply_obs_snapshot(state, scene_name=None, sources=None, status=None):
    state.setdefault("obs", {})
    state["obs"].setdefault("scene", "OBS: unknown")
    state["obs"].setdefault("sources", [])

    if status is not None:
        state["obs"]["scene"] = status
    if scene_name is not None:
        state["obs"]["scene"] = scene_name
    if sources is not None:
        state["obs"]["sources"] = sources

    state["updated"] = time.time()

async def obs_worker(state):
    while True:
        try:
            mode = (os.getenv("OBS_MODE", "direct") or "direct").strip().lower()

            if mode == "off":
                apply_obs_snapshot(state, status="OBS: disabled", sources=[])
                await asyncio.sleep(5)
                continue

            if mode == "agent":
                apply_obs_snapshot(state, status="OBS: agent mode (waiting for agent)", sources=[])
                await asyncio.sleep(3)
                continue

            from obsws_python import ReqClient

            url = os.getenv("OBS_WS_URL", "ws://127.0.0.1:4455")
            pwd = os.getenv("OBS_WS_PASSWORD", "")

            hp = url.replace("ws://", "").replace("wss://", "").split("/", 1)[0]
            host, port = (hp.split(":", 1)[0], int(hp.split(":", 1)[1])) if ":" in hp else (hp, 4455)

            if not pwd:
                apply_obs_snapshot(state, status="OBS: password not set", sources=[])
                await asyncio.sleep(3)
                continue

            c = ReqClient(host=host, port=port, password=pwd, timeout=2)
            s = c.get_current_program_scene()
            scene = getattr(s, "current_program_scene_name", None) or "Unknown"
            apply_obs_snapshot(state, scene_name=scene, sources=[], status=None)

        except Exception as e:
            apply_obs_snapshot(state, status=f"OBS: disconnected ({type(e).__name__})")
        await asyncio.sleep(2)
```

## File layout (truncated)
- .env (752 bytes)
- .env.example (270 bytes)
- ai/engine.py (2464 bytes)
- ai/engine_v2.py (2223 bytes)
- ai/engine_v2.py.bak.20251222T035031Z (2085 bytes)
- ai/index/resource_index.py (2307 bytes)
- ai/logic_machine.py (12731 bytes)
- ai/logic_machine.py.bak.20251222T035023Z (7186 bytes)
- ai/models.py (2557 bytes)
- ai/models.py.bak.20251222T035009Z (2096 bytes)
- ai/planners/topic_plan.py (1023 bytes)
- ai/providers/base.py (230 bytes)
- ai/providers/rulebased.py (4938 bytes)
- ai/signals/chat_signals.py (2569 bytes)
- ai/signals/resource_signals.py (834 bytes)
- ai/types.py (722 bytes)
- api/__init__.py (0 bytes)
- api/ai_routes.py (1898 bytes)
- api/app.py (12024 bytes)
- api/app.py.bak.20251222T023356Z (8689 bytes)
- api/app.py.bak.20251222T032139Z (10084 bytes)
- api/app.py.bak.20251222T032228Z (9839 bytes)
- api/app.py.bak.20251222T035559Z (11023 bytes)
- api/app.py.bak.20251222T035645Z (11888 bytes)
- api/app.py.bak.20251222T035747Z.pre-transcript (11888 bytes)
- api/app.py.bak.20251222T035843Z.fix-json-indent (11888 bytes)
- api/app.py.bak.20251222T035930Z.add-transcript-v1 (11768 bytes)
- api/app.py.bak.20251222T035939Z.wire-transcript-into-state (12934 bytes)
- api/app.py.bak.20251222T040325Z.fix-home-route (12982 bytes)
- api/app.py.bak.20251222T040504Z.fix-head-500-v2 (10008 bytes)
- api/app.py.bak.20251222T041824Z.boot-banner (9971 bytes)
- api/app.py.bak.20251222T044305Z.ipad-safe (11396 bytes)
- api/app.py.bak.20251222T051819Z (12024 bytes)
- api/app.py.bak.20251222T051929Z (12024 bytes)
- api/app.py.bak.20251222T052141Z (12024 bytes)
- api/app.py.bak.20251222T142333Z (12024 bytes)
- api/chat_routes.py (3167 bytes)
- api/extensions.py (5118 bytes)
- api/store.py (1290 bytes)
- api/ui_home.py (17753 bytes)
- api/ui_home.py.bak.20251222T031730Z (9194 bytes)
- api/ui_home.py.bak.20251222T035039Z (10968 bytes)
- api/ui_home.py.bak.20251222T035718Z (12252 bytes)
- api/ui_home.py.bak.20251222T035735Z (15596 bytes)
- api/ui_home.py.bak.20251222T040637Z.debug-banner (15596 bytes)
- api/ui_home.py.bak.20251222T041155Z.js-error-banner (16607 bytes)
- api/ui_home.py.bak.20251222T041306Z.boot-jsErrors (16607 bytes)
- api/ui_home.py.bak.20251222T041414Z.add-boot-banner (16607 bytes)
- api/ui_home.py.bak.20251222T041459Z.disable-video (16919 bytes)
- api/ui_home.py.bak.20251222T042541Z.bootv10 (16954 bytes)
- api/ui_home.py.bak.20251222T142632Z (17784 bytes)
- api/ui_home.py.bak.20251222T142930Z (17784 bytes)
- api/ui_home.py.bak.20251222T142937Z (17753 bytes)
- api/ui_ipad.py (2852 bytes)
- collector/__init__.py (0 bytes)
- collector/chat/base.py (1056 bytes)
- collector/chat/manager.py (1877 bytes)
- collector/chat/twitch.py (2763 bytes)
- collector/chat/youtube.py (2297 bytes)
- collector/obs_ws.py (1954 bytes)
- collector/transcribe_hls.py (7139 bytes)
- data/stream.json (91 bytes)
- data/transcript.json (6579 bytes)
- diag/REPORT.txt (2860 bytes)
- diag/app/api/__init__.py (0 bytes)
- diag/app/api/app.py (12024 bytes)
- diag/app/api/ui_home.py (17753 bytes)
- diag/app/collector/transcribe_hls.py (7139 bytes)
- diag/app/curl_checks.txt (8774 bytes)
- diag/app/env_all.txt (2203 bytes)
- diag/app/ps_filtered.txt (575 bytes)
- diag/app/pwd.txt (21 bytes)
- diag/app/python_sanity.txt (1353 bytes)
- diag/app/transcript.json (6303 bytes)
- diag/fs/ls_var_www_html.txt (239 bytes)
- diag/fs/ls_var_www_html_hls.txt (490 bytes)
- diag/fs/stat_www_hls.txt (770 bytes)
- diag/fs/tree_maxdepth3.txt (3517 bytes)
- diag/logs/journal_nginx.txt (7797 bytes)
- diag/logs/journal_stream-copilot.txt (31447 bytes)
- diag/logs/journal_transcribe.txt (124 bytes)
- diag/logs/nginx_access_tail.txt (61742 bytes)
- diag/logs/nginx_error_tail.txt (45758 bytes)
- diag/net/iptables_S.txt (51 bytes)
- diag/net/ss_antp.txt (15908 bytes)
- diag/net/ss_lntup.txt (1924 bytes)
- diag/net/ufw_status.txt (17 bytes)
- diag/nginx/conf.d/stream-copilot-nocache.conf.DISABLED.20251222T051240Z (847 bytes)
- diag/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045758Z (779 bytes)
- diag/nginx/conf.d/stream-copilot-nocache.conf.bak.20251222T045959Z (832 bytes)
- diag/nginx/conf.d/stream-copilot.conf (690 bytes)
- diag/nginx/conf.d/stream-copilot.conf.bak.20251222T144402Z (642 bytes)
- diag/nginx/ls_conf_d.txt (515 bytes)
- diag/nginx/ls_etc_nginx.txt (1034 bytes)
- diag/nginx/ls_sites_enabled.txt (98 bytes)
- diag/nginx/nginx-T.txt (8509 bytes)
- diag/nginx/rtmp.conf (264 bytes)
- diag/nginx/snippets/fastcgi-php.conf (423 bytes)
- diag/nginx/snippets/snakeoil.conf (217 bytes)
- diag/nginx/snippets/stream-copilot-hls.conf (222 bytes)
- diag/systemd/status.txt (4527 bytes)
- diag/systemd/stream-copilot-transcribe.service (624 bytes)
- diag/systemd/stream-copilot.service (327 bytes)
- diag/systemd/systemctl_cat_stream-copilot-transcribe.service.txt (680 bytes)
- diag/systemd/systemctl_cat_stream-copilot.service.txt (372 bytes)
- diag-20251222T144706Z.tgz (35163 bytes)
- outputs/ui.html (4516 bytes)
- s -lntp | grep :22 (2121 bytes)
- tools/make_report.py (5141 bytes)
- ui/index.html (14726 bytes)

## Recent stream-copilot logs
```text
Dec 22 18:55:15 localhost uvicorn[283050]:         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Dec 22 18:55:15 localhost uvicorn[283050]:     )
Dec 22 18:55:15 localhost uvicorn[283050]:     ^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/main.py", line 594, in run
Dec 22 18:55:15 localhost uvicorn[283050]:     server.run()
Dec 22 18:55:15 localhost uvicorn[283050]:     ~~~~~~~~~~^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/server.py", line 67, in run
Dec 22 18:55:15 localhost uvicorn[283050]:     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/usr/lib/python3.13/asyncio/runners.py", line 195, in run
Dec 22 18:55:15 localhost uvicorn[283050]:     return runner.run(main)
Dec 22 18:55:15 localhost uvicorn[283050]:            ~~~~~~~~~~^^^^^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/usr/lib/python3.13/asyncio/runners.py", line 118, in run
Dec 22 18:55:15 localhost uvicorn[283050]:     return self._loop.run_until_complete(task)
Dec 22 18:55:15 localhost uvicorn[283050]:            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/usr/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
Dec 22 18:55:15 localhost uvicorn[283050]:     return future.result()
Dec 22 18:55:15 localhost uvicorn[283050]:            ~~~~~~~~~~~~~^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/server.py", line 71, in serve
Dec 22 18:55:15 localhost uvicorn[283050]:     await self._serve(sockets)
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/server.py", line 78, in _serve
Dec 22 18:55:15 localhost uvicorn[283050]:     config.load()
Dec 22 18:55:15 localhost uvicorn[283050]:     ~~~~~~~~~~~^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/config.py", line 439, in load
Dec 22 18:55:15 localhost uvicorn[283050]:     self.loaded_app = import_from_string(self.app)
Dec 22 18:55:15 localhost uvicorn[283050]:                       ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/venv/lib/python3.13/site-packages/uvicorn/importer.py", line 19, in import_from_string
Dec 22 18:55:15 localhost uvicorn[283050]:     module = importlib.import_module(module_str)
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/usr/lib/python3.13/importlib/__init__.py", line 88, in import_module
Dec 22 18:55:15 localhost uvicorn[283050]:     return _bootstrap._gcd_import(name[level:], package, level)
Dec 22 18:55:15 localhost uvicorn[283050]:            ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
Dec 22 18:55:15 localhost uvicorn[283050]:   File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
Dec 22 18:55:15 localhost uvicorn[283050]:   File "/root/stream-copilot/api/app.py", line 13, in <module>
Dec 22 18:55:15 localhost uvicorn[283050]:     from collector.obs_ws import obs_worker
Dec 22 18:55:15 localhost uvicorn[283050]: ImportError: cannot import name 'obs_worker' from 'collector.obs_ws' (/root/stream-copilot/collector/obs_ws.py)
Dec 22 18:55:15 localhost systemd[1]: stream-copilot.service: Main process exited, code=exited, status=1/FAILURE
Dec 22 18:55:15 localhost systemd[1]: stream-copilot.service: Failed with result 'exit-code'.
Dec 22 18:55:17 localhost systemd[1]: stream-copilot.service: Scheduled restart job, restart counter is at 22.
Dec 22 18:55:17 localhost systemd[1]: Started stream-copilot.service - Stream Co-Pilot API.
Dec 22 18:55:17 localhost uvicorn[283073]: INFO:     Started server process [283073]
Dec 22 18:55:17 localhost uvicorn[283073]: INFO:     Waiting for application startup.
Dec 22 18:55:17 localhost uvicorn[283073]: INFO:     Application startup complete.
Dec 22 18:55:17 localhost uvicorn[283073]: INFO:     Uvicorn running on http://0.0.0.0:8811 (Press CTRL+C to quit)
Dec 22 18:57:32 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "HEAD / HTTP/1.1" 200 OK
Dec 22 18:57:32 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "GET / HTTP/1.1" 200 OK
Dec 22 18:57:33 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "HEAD /_next HTTP/1.1" 404 Not Found
Dec 22 18:57:33 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "POST / HTTP/1.1" 405 Method Not Allowed
Dec 22 18:57:33 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "POST /_next HTTP/1.1" 404 Not Found
Dec 22 18:58:03 localhost uvicorn[283073]: INFO:     146.70.185.32:0 - "HEAD / HTTP/1.1" 200 OK
Dec 22 19:03:55 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "HEAD / HTTP/1.1" 200 OK
Dec 22 19:03:55 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:03:55 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "HEAD /_next HTTP/1.1" 404 Not Found
Dec 22 19:03:55 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "POST / HTTP/1.1" 405 Method Not Allowed
Dec 22 19:03:55 localhost uvicorn[283073]: INFO:     65.87.7.112:0 - "POST /_next HTTP/1.1" 404 Not Found
Dec 22 19:06:57 localhost uvicorn[283073]: INFO:     50.16.249.26:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:12:56 localhost uvicorn[283073]: INFO:     146.59.34.59:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:40 localhost uvicorn[283073]: INFO:     34.248.137.227:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:40 localhost uvicorn[283073]: INFO:     34.248.137.227:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:40 localhost uvicorn[283073]: INFO:     34.248.137.227:0 - "GET /favicon.ico HTTP/1.1" 404 Not Found
Dec 22 19:13:41 localhost uvicorn[283073]: INFO:     34.248.137.227:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:41 localhost uvicorn[283073]: INFO:     34.248.137.227:0 - "HEAD /favicon.ico HTTP/1.1" 404 Not Found
Dec 22 19:13:57 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //xmlrpc.php?rsd HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //blog/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //web/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //wordpress/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //website/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //wp/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //news/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //2018/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //2019/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //shop/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //wp1/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //test/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //media/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //wp2/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //site/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //cms/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:13:58 localhost uvicorn[283073]: INFO:     142.248.80.192:0 - "GET //sito/wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found
Dec 22 19:37:38 localhost systemd[1]: Stopping stream-copilot.service - Stream Co-Pilot API...
Dec 22 19:37:38 localhost uvicorn[283073]: INFO:     Shutting down
Dec 22 19:37:38 localhost uvicorn[283073]: INFO:     Waiting for application shutdown.
Dec 22 19:37:38 localhost uvicorn[283073]: INFO:     Application shutdown complete.
Dec 22 19:37:38 localhost uvicorn[283073]: INFO:     Finished server process [283073]
Dec 22 19:37:38 localhost systemd[1]: stream-copilot.service: Deactivated successfully.
Dec 22 19:37:38 localhost systemd[1]: Stopped stream-copilot.service - Stream Co-Pilot API.
Dec 22 19:37:38 localhost systemd[1]: stream-copilot.service: Consumed 3.725s CPU time, 33.5M memory peak.
Dec 22 19:37:38 localhost systemd[1]: Started stream-copilot.service - Stream Co-Pilot API.
Dec 22 19:37:39 localhost uvicorn[295603]: INFO:     Started server process [295603]
Dec 22 19:37:39 localhost uvicorn[295603]: INFO:     Waiting for application startup.
Dec 22 19:37:39 localhost uvicorn[295603]: INFO:     Application startup complete.
Dec 22 19:37:39 localhost uvicorn[295603]: INFO:     Uvicorn running on http://0.0.0.0:8811 (Press CTRL+C to quit)
Dec 22 19:39:18 localhost uvicorn[295603]: INFO:     47.231.165.111:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:39:40 localhost uvicorn[295603]: INFO:     127.0.0.1:35576 - "GET /api/state HTTP/1.1" 200 OK
Dec 22 19:40:07 localhost uvicorn[295603]: INFO:     172.239.37.126:0 - "GET /api/state HTTP/1.1" 200 OK
Dec 22 19:40:19 localhost systemd[1]: Stopping stream-copilot.service - Stream Co-Pilot API...
Dec 22 19:40:19 localhost uvicorn[295603]: INFO:     Shutting down
Dec 22 19:40:19 localhost uvicorn[295603]: INFO:     Waiting for application shutdown.
Dec 22 19:40:19 localhost uvicorn[295603]: INFO:     Application shutdown complete.
Dec 22 19:40:19 localhost uvicorn[295603]: INFO:     Finished server process [295603]
Dec 22 19:40:19 localhost systemd[1]: stream-copilot.service: Deactivated successfully.
Dec 22 19:40:19 localhost systemd[1]: Stopped stream-copilot.service - Stream Co-Pilot API.
Dec 22 19:40:19 localhost systemd[1]: Started stream-copilot.service - Stream Co-Pilot API.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Started server process [296326]
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Waiting for application startup.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Application startup complete.
Dec 22 19:40:19 localhost uvicorn[296326]: INFO:     Uvicorn running on http://0.0.0.0:8811 (Press CTRL+C to quit)
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET /favicon.ico HTTP/1.1" 404 Not Found
Dec 22 19:40:47 localhost uvicorn[296326]: INFO:     98.94.18.225:0 - "GET /favicon.png HTTP/1.1" 404 Not Found
Dec 22 19:41:29 localhost uvicorn[296326]: INFO:     47.231.165.111:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:42:13 localhost uvicorn[296326]: INFO:     141.51.110.126:0 - "GET / HTTP/1.1" 200 OK
Dec 22 19:46:59 localhost uvicorn[296326]: INFO:     127.0.0.1:40836 - "GET /api/state HTTP/1.1" 200 OK
Dec 22 19:46:59 localhost uvicorn[296326]: INFO:     172.239.37.126:0 - "GET /api/state HTTP/1.1" 200 OK
```
