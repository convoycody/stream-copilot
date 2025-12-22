#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

ROOT = Path("/root/stream-copilot")
OUT = ROOT / "PROJECT_REPORT.md"

SECRET_KEY_HINTS = ("KEY", "TOKEN", "PASSWORD", "SECRET", "OAUTH", "PRIVATE", "PASS")

def sh(cmd: List[str], timeout: int = 20) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 99, "", f"{type(e).__name__}: {e}"

def redact_env_line(line: str) -> str:
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line.strip())
    if not m:
        return line.rstrip()
    k, v = m.group(1), m.group(2)
    if any(h in k.upper() for h in SECRET_KEY_HINTS) and v != "":
        return f"{k}=<REDACTED>"
    return f"{k}={v}"

def read_env(path: Path) -> List[str]:
    if not path.exists():
        return ["(missing)"]
    out: List[str] = []
    for raw in path.read_text(errors="replace").splitlines():
        if raw.strip().startswith("#") or raw.strip() == "":
            out.append(raw.rstrip())
        else:
            out.append(redact_env_line(raw))
    return out

def head(path: Path, n: int = 120) -> str:
    if not path.exists():
        return "(missing)"
    txt = path.read_text(errors="replace").splitlines()
    return "\n".join(txt[:n])

def file_tree(root: Path, max_files: int = 220) -> List[str]:
    lines: List[str] = []
    count = 0
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts or "venv" in p.parts or "__pycache__" in p.parts:
            continue
        if p.is_dir():
            continue
        rel = p.relative_to(root)
        size = p.stat().st_size
        lines.append(f"- {rel} ({size} bytes)")
        count += 1
        if count >= max_files:
            lines.append(f"- ... (truncated at {max_files} files)")
            break
    return lines

def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sections: List[str] = []
    sections.append(f"# Stream Co-Pilot – Server Report\n\nGenerated: **{now}**\n")

    rc, uname, _ = sh(["uname", "-a"])
    rc, uptime, _ = sh(["uptime"])
    sections.append("## System\n```text\n" + (uname or "") + "\n" + (uptime or "") + "\n```\n")

    sections.append("## Services\n")
    for svc in ["nginx", "stream-copilot"]:
        _, out, err = sh(["systemctl", "is-active", svc])
        sections.append(f"- {svc}: `{out or err}`")
    sections.append("\n")

    _, out, err = sh(["systemctl", "--no-pager", "-l", "status", "stream-copilot"])
    sections.append("### stream-copilot status\n```text\n" + (out or err) + "\n```\n")

    _, out, err = sh(["systemctl", "cat", "stream-copilot.service"])
    sections.append("### stream-copilot unit\n```text\n" + (out or err) + "\n```\n")

    _, out, err = sh(["ss", "-lntp"])
    filtered = []
    for line in (out.splitlines() if out else []):
        if any(f":{p}" in line for p in [22, 80, 443, 8811]):
            filtered.append(line)
    sections.append("## Listening ports (filtered)\n```text\n" + ("\n".join(filtered) if filtered else "(none matched)") + "\n```\n")

    _, out, err = sh(["ufw", "status", "numbered"])
    sections.append("## Firewall (ufw)\n```text\n" + (out or err) + "\n```\n")

    _, out, err = sh(["bash", "-lc", r"rg -n --no-heading 'proxy_pass|upstream|8811|stream-copilot|streamcopilot' /etc/nginx/sites-enabled /etc/nginx/conf.d /etc/nginx/nginx.conf || true"])
    sections.append("## Nginx proxy targets\n```text\n" + (out or err) + "\n```\n")

    _, out1, err1 = sh(["bash", "-lc", "curl -s http://127.0.0.1:8811/api/state | head -c 1400"])
    _, out2, err2 = sh(["bash", "-lc", "curl -s https://streamcopilot.org/api/state | head -c 1400"])
    sections.append("## API health\n")
    sections.append("### Local\n```json\n" + (out1 or err1) + "\n```\n")
    sections.append("### Public\n```json\n" + (out2 or err2) + "\n```\n")

    sections.append("## Repo snapshot\n")
    if (ROOT / ".git").exists():
        _, out, err = sh(["bash", "-lc", "git rev-parse --short HEAD && echo && git status --porcelain=v1 && echo && git remote -v || true"])
        sections.append("```text\n" + (out or err) + "\n```\n")
    else:
        sections.append("(not a git repo here)\n")

    sections.append("## Environment (.env redacted)\n```text\n" + "\n".join(read_env(ROOT / '.env')) + "\n```\n")

    sections.append("## Key files (first lines)\n")
    for p in ["api/app.py", "collector/obs_ws.py"]:
        sections.append(f"### {p}\n```text\n{head(ROOT / p, 140)}\n```\n")

    sections.append("## File layout (truncated)\n" + "\n".join(file_tree(ROOT)) + "\n")

    _, out, err = sh(["bash", "-lc", "journalctl -u stream-copilot -n 120 --no-pager || true"], timeout=30)
    sections.append("## Recent stream-copilot logs\n```text\n" + (out or err) + "\n```\n")

    OUT.write_text("\n".join(sections))
    print(str(OUT))

if __name__ == "__main__":
    main()
