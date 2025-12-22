def render_ipad_home(request=None, state=None) -> str:
    # Ultra-safe HTML for iPad Safari: no video tag, minimal JS, no fancy layout.
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Stream Co-Pilot (iPad Safe)</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0b0b10;color:#eaeaf2}
    .top{position:sticky;top:0;background:#12121a;border-bottom:1px solid #222;padding:12px 14px;z-index:9999}
    .badge{display:inline-block;padding:3px 10px;border-radius:999px;background:#064e3b;color:#fff;font-size:12px}
    .wrap{padding:14px}
    .card{background:#12121a;border:1px solid #222;border-radius:12px;padding:12px;margin:12px 0}
    .muted{opacity:.75;font-size:12px}
    pre{white-space:pre-wrap;word-break:break-word;margin:0}
    button{background:#1f1f2b;color:#eaeaf2;border:1px solid #333;border-radius:10px;padding:10px 12px;font-weight:700}
  </style>
</head>
<body>
  <div class="top">
    <div><span class="badge">iPad Safe UI</span></div>
    <div class="muted">If this loads, the blank issue is in the main UI (video/JS/layout). We’ll fix that next.</div>
  </div>

  <div class="wrap">
    <div class="card">
      <div style="display:flex;gap:10px;align-items:center;justify-content:space-between">
        <div>
          <div style="font-weight:800">Stream Co-Pilot</div>
          <div class="muted" id="status">Loading…</div>
        </div>
        <button onclick="loadNow()">Refresh</button>
      </div>
    </div>

    <div class="card">
      <div style="font-weight:800;margin-bottom:8px">/api/state</div>
      <pre id="state">—</pre>
    </div>

    <div class="card">
      <div style="font-weight:800;margin-bottom:8px">JS errors</div>
      <pre id="errs" class="muted">—</pre>
    </div>
  </div>

<script>
(function(){
  const $ = (id)=>document.getElementById(id);
  function logErr(msg){ $("errs").textContent = ( $("errs").textContent==="—" ? "" : $("errs").textContent + "\\n") + msg; }
  window.addEventListener("error", e=>logErr("[error] " + (e.message||"") ));
  window.addEventListener("unhandledrejection", e=>logErr("[promise] " + (e.reason && (e.reason.message||e.reason)) ));

  async function loadNow(){
    try{
      $("status").textContent = "Fetching state…";
      const r = await fetch("/api/state", {cache:"no-store"});
      const j = await r.json();
      $("status").textContent = "OK • updated=" + (j.updated ? new Date(j.updated*1000).toLocaleTimeString() : "—");
      $("state").textContent = JSON.stringify(j, null, 2);
    }catch(e){
      $("status").textContent = "Failed to load state";
      logErr(String(e && e.message ? e.message : e));
    }
  }
  window.loadNow = loadNow;
  loadNow();
})();
</script>
</body>
</html>"""
