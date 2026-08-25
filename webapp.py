import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

from breath_tools import get_practice_for_heart_rate, get_pranayama_for_heart_rate
from garmin_client import GarminError, fetch_heart_rate
from garmin_service import login_and_fetch_heart_rate

load_dotenv(Path(__file__).with_name(".env"))

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prana Pulse</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
:root { --ink:#17221d; --muted:#68756e; --paper:#f4f1e8; --sage:#d9e5d2; --green:#2e6749; --coral:#df7255; --line:#cbd3c8; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:var(--paper); font-family:Manrope, sans-serif; }
main { max-width:1120px; min-height:100vh; margin:auto; padding:34px 28px 60px; }
nav { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); padding-bottom:20px; }
.brand { font-size:18px; font-weight:800; letter-spacing:.02em; }
.brand span { color:var(--coral); }
.status { display:flex; align-items:center; gap:8px; font:12px 'DM Mono', monospace; color:var(--muted); }
.dot { width:8px; height:8px; border-radius:50%; background:var(--coral); }.dot.on { background:#5a9b6c; }
.hero { display:grid; grid-template-columns:1.15fr .85fr; gap:70px; padding:90px 0 70px; align-items:end; }
.kicker { color:var(--coral); font:12px 'DM Mono', monospace; text-transform:uppercase; letter-spacing:.12em; }
h1 { max-width:650px; font-size:clamp(48px, 7vw, 86px); line-height:.96; letter-spacing:-.06em; margin:16px 0 24px; }
.lede { max-width:510px; color:var(--muted); font-size:17px; line-height:1.6; }
.panel { background:var(--sage); padding:28px; border-radius:6px; }
.panel h2 { margin:0 0 24px; font-size:14px; text-transform:uppercase; letter-spacing:.08em; }
.bpm { font-size:76px; line-height:1; font-weight:800; letter-spacing:-.07em; }.bpm small { font-size:16px; letter-spacing:0; color:var(--muted); }
.meta { color:var(--muted); font:12px 'DM Mono', monospace; margin-top:10px; }
button { border:0; border-radius:3px; background:var(--green); color:white; padding:14px 18px; font:700 13px Manrope, sans-serif; cursor:pointer; margin-top:25px; } button:hover { background:#234e38; } button:disabled { opacity:.55; cursor:wait; }
button.secondary { background:transparent; color:var(--green); border:1px solid var(--green); margin-left:8px; }
.recommendation { border-top:1px solid var(--line); padding-top:30px; }.recommendation h2 { font-size:13px; color:var(--coral); text-transform:uppercase; letter-spacing:.1em; }.practice { font-size:34px; font-weight:800; letter-spacing:-.04em; margin:10px 0; }.detail { color:var(--muted); line-height:1.6; }.session-limit { color:var(--muted); font:12px 'DM Mono', monospace; margin-top:18px; }
.visualizer { display:flex; align-items:center; gap:34px; margin-top:28px; }.breath-orb { width:190px; height:190px; border:1px solid var(--green); border-radius:50%; display:grid; place-items:center; flex:0 0 auto; }.breath-orb::before { content:""; width:76px; height:76px; background:var(--coral); border-radius:50%; animation:breathe var(--cycle-duration, 16s) ease-in-out infinite; }.phase { color:var(--green); font:18px 'DM Mono', monospace; text-transform:uppercase; letter-spacing:.08em; }.phase-time { color:var(--ink); font:800 48px 'DM Mono', monospace; line-height:1; margin-top:10px; }.rhythm { color:var(--muted); font-size:13px; line-height:1.5; margin-top:12px; }.breath-controls { display:flex; gap:8px; }.breath-controls button { margin-top:18px; padding:10px 13px; }.visualizer.idle .breath-orb::before, .visualizer.paused .breath-orb::before { animation-play-state:paused; transform:scale(.65); } .visualizer.paused .breath-orb::before { transform:scale(1); } @keyframes breathe { 0%,25%{transform:scale(.65)} 50%,75%{transform:scale(1.35)} 100%{transform:scale(.65)} }
footer { border-top:1px solid var(--line); padding-top:18px; color:var(--muted); font:11px 'DM Mono', monospace; }
@media (max-width:760px) { main{padding:24px 20px 40px}.hero{grid-template-columns:1fr;gap:36px;padding:62px 0 48px}h1{font-size:54px}.panel{padding:22px}.bpm{font-size:64px}.visualizer{gap:20px}.breath-orb{width:150px;height:150px}.breath-orb::before{width:60px;height:60px}.phase-time{font-size:38px} }
</style>
</head>
<body>
<main>
<nav><div class="brand">PRANA<span>/</span>PULSE</div><div class="status"><i class="dot" id="dot"></i><span id="status">GARMIN NOT CONNECTED</span></div></nav>
<section class="hero">
<div><div class="kicker">Hourly gentle awareness</div><h1>Breathe with your body's signal.</h1><p class="lede">Connect Garmin to make space for a short, gentle breathing pause. Your data stays on this local app.</p></div>
<div class="panel"><h2>Current pulse</h2><div class="bpm" id="bpm">-- <small>bpm</small></div><div class="meta" id="timestamp">Waiting for Garmin</div><button id="connect" onclick="connectGarmin()">Connect Garmin</button><button class="secondary" id="refresh" onclick="refreshPulse()">Refresh</button></div>
</section>
<section class="recommendation"><h2>Next practice</h2><div class="practice" id="practice">Connect Garmin to begin</div><p class="detail" id="detail">The app will suggest a calming, balancing, or energizing practice each hour based on your latest reading.</p><div class="session-limit">Gentle awareness · <span id="session-time">90</span>s remaining</div><div class="visualizer idle" id="visualizer"><div class="breath-orb"></div><div><div class="phase" id="phase">Ready when you are</div><div class="phase-time" id="phase-time">Follow the rhythm</div><div class="rhythm" id="rhythm">Your breathing rhythm will appear here.</div><div class="breath-controls"><button id="pause" onclick="toggleBreathPause()" disabled>Pause</button><button class="secondary" onclick="restartBreathGuide()" disabled id="restart">Restart</button></div></div></div></section>
<footer>LOCAL SESSION · HEART RATE IS NOT MEDICAL ADVICE · STOP IF YOU FEEL UNWELL</footer>
</main>
<script>
async function connectGarmin() { const button=document.getElementById('connect'); button.disabled=true; button.textContent='Opening login...'; try { const response=await fetch('/api/login'); const data=await response.json(); if (data.url) window.location.href=data.url; else alert(data.error); } finally { button.disabled=false; button.textContent='Connect Garmin'; } }
async function refreshPulse() { const button=document.getElementById('refresh'); button.disabled=true; try { const response=await fetch('/api/heart-rate'); const data=await response.json(); if (data.error) { document.getElementById('status').textContent='GARMIN NOT CONNECTED'; return; } document.getElementById('dot').classList.add('on'); document.getElementById('status').textContent='GARMIN CONNECTED'; document.getElementById('bpm').innerHTML=data.bpm+' <small>bpm</small>'; document.getElementById('timestamp').textContent=data.timestamp || 'Latest reading'; document.getElementById('practice').textContent=data.practice; document.getElementById('detail').textContent=data.detail; document.getElementById('visualizer').classList.remove('idle'); document.getElementById('rhythm').textContent=data.phases.map(phase => phase[0]+' '+phase[1]+'s').join(' / '); startBreathGuide(data.phases); } finally { button.disabled=false; } }
let breathTimer;
let countdownTimer;
let breathPhases=[];
let breathIndex=0;
let breathRemaining=0;
let sessionRemaining=90;
let breathPaused=false;
function startBreathGuide(phases) { clearTimeout(breathTimer); clearInterval(countdownTimer); breathPhases=phases; breathIndex=0; breathRemaining=0; sessionRemaining=90; breathPaused=false; document.getElementById('session-time').textContent=sessionRemaining; document.getElementById('visualizer').classList.remove('idle','paused'); document.getElementById('pause').disabled=false; document.getElementById('restart').disabled=false; document.getElementById('pause').textContent='Pause'; document.getElementById('visualizer').style.setProperty('--cycle-duration', phases.reduce((total, phase) => total+phase[1], 0)+'s'); runBreathPhase(); }
function finishBreathGuide() { clearTimeout(breathTimer); clearInterval(countdownTimer); breathRemaining=0; sessionRemaining=0; document.getElementById('session-time').textContent='0'; document.getElementById('phase').textContent='Session complete'; document.getElementById('phase-time').textContent='0'; document.getElementById('pause').disabled=true; document.getElementById('visualizer').classList.add('idle'); }
function runBreathPhase() { clearTimeout(breathTimer); clearInterval(countdownTimer); if (breathPaused || !breathPhases.length || sessionRemaining <= 0) { if (sessionRemaining <= 0) finishBreathGuide(); return; } const phase=breathPhases[breathIndex % breathPhases.length]; breathRemaining=breathRemaining || phase[1]; document.getElementById('phase').textContent=phase[0]; document.getElementById('phase-time').textContent=breathRemaining; countdownTimer=setInterval(()=>{ breathRemaining-=1; sessionRemaining-=1; document.getElementById('session-time').textContent=sessionRemaining; if (breathRemaining > 0) document.getElementById('phase-time').textContent=breathRemaining; if (sessionRemaining <= 0) finishBreathGuide(); }, 1000); breathTimer=setTimeout(()=>{ breathIndex++; breathRemaining=0; runBreathPhase(); }, breathRemaining*1000); }
function toggleBreathPause() { if (!breathPhases.length) return; breathPaused=!breathPaused; document.getElementById('visualizer').classList.toggle('paused', breathPaused); document.getElementById('pause').textContent=breathPaused ? 'Resume' : 'Pause'; if (breathPaused) { clearTimeout(breathTimer); clearInterval(countdownTimer); } else { runBreathPhase(); } }
function restartBreathGuide() { if (!breathPhases.length) return; breathIndex=0; breathRemaining=0; sessionRemaining=90; breathPaused=false; document.getElementById('session-time').textContent=sessionRemaining; document.getElementById('visualizer').classList.remove('idle','paused'); document.getElementById('pause').disabled=false; document.getElementById('pause').textContent='Pause'; runBreathPhase(); }
if (new URLSearchParams(window.location.search).has('connected')) refreshPulse();
setInterval(refreshPulse, 60 * 60 * 1000);
</script>
</body></html>"""

DETAILS = {
    "Nadi Shodhana": "A balancing practice for a pulse that is running high. Keep the breath smooth and unforced.",
    "Bhastrika": "An energizing practice for a low resting pulse. Skip it if you feel dizzy or unwell.",
    "Bhramari": "A settling humming practice for a steady pulse. Let the exhale be longer than the inhale.",
}


def _login_url():
    if os.getenv("GARMIN_PROVIDER", "garminconnect").lower() == "garminconnect":
        return "/garmin/login", None
    missing = [name for name in ("GARMIN_AUTHORIZATION_URL", "GARMIN_TOKEN_URL", "GARMIN_CLIENT_ID") if not os.getenv(name)]
    if missing:
        return None, "Add Garmin OAuth settings to .env: " + ", ".join(missing)
    return "/garmin/login", None


class AppHandler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200, headers=None):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/login":
            url, error = _login_url()
            self._json({"url": url, "error": error}, 400 if error else 200)
        elif path == "/garmin/login":
            body = b"""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Connect Garmin</title><style>body{font-family:Arial,sans-serif;background:#f4f1e8;color:#17221d;max-width:520px;margin:80px auto;padding:24px}form{display:grid;gap:14px}input{padding:13px;border:1px solid #cbd3c8;border-radius:3px;font-size:16px}button{padding:14px;background:#2e6749;color:white;border:0;border-radius:3px;font-weight:bold;font-size:14px}</style></head><body><h1>Connect Garmin</h1><p>Credentials are sent only to Garmin Connect through the local app and are not saved.</p><form method='post'><label>Email<input name='email' type='email' required autocomplete='username'></label><label>Password<input name='password' type='password' required autocomplete='current-password'></label><button>Sign in to Garmin</button></form></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/heart-rate":
            try:
                reading = fetch_heart_rate()
                practice = get_practice_for_heart_rate(reading.bpm)
                self._json({"bpm": reading.bpm, "timestamp": reading.timestamp, "practice": practice["name"], "detail": practice["description"], "phases": practice["phases"]})
            except GarminError as error:
                self._json({"error": str(error)}, 400)
        else:
            self._json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        return

    def do_POST(self):  # noqa: N802
        if urlparse(self.path).path != "/garmin/login":
            self._json({"error": "Not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        values = parse_qs(self.rfile.read(length).decode())
        email = values.get("email", [""])[0]
        password = values.get("password", [""])[0]
        try:
            login_and_fetch_heart_rate(email, password)
            self.send_response(302)
            self.send_header("Location", "/?connected=1")
            self.end_headers()
        except GarminError as error:
            self._json({"error": str(error)}, 400)


def main():
    port = int(os.getenv("WEBAPP_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    url = f"http://localhost:{port}"
    print(f"Prana Pulse is running at {url}")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
