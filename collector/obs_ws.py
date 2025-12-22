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
