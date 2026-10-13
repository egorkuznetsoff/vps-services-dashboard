#!/usr/bin/env python3
"""Plan — карта сервисов VPS. Порт 8083, за nginx на /plan/."""
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

PORT = 8083

# systemd_unit=None -> нет юнита (статика или системный процесс без unit-статуса)
SERVICES = [
    {
        "id": "awg-panel",
        "name": "AWG Panel",
        "description": "Панель администратора AmneziaWG VPN — управление ключами, тарифами, deep-link для клиента.",
        "description_en": "AmneziaWG VPN admin panel — key management, tariffs, client deep-link generation.",
        "stack": ["Python 3", "Flask", "PostgreSQL"],
        "port": 8084,
        "url": "/awg/",
        "systemd_unit": "awg-panel.service",
        "category": "panel",
    },
    {
        "id": "awg-monitor",
        "name": "AWG Monitor",
        "description": "Фоновый монитор качества соединений AmneziaWG (без веб-морды).",
        "description_en": "Background AmneziaWG connection-quality monitor (no web UI).",
        "stack": ["Python 3"],
        "port": None,
        "url": None,
        "systemd_unit": "awg-monitor.service",
        "category": "panel",
    },
    {
        "id": "diet",
        "name": "Diet AI (Slimfy)",
        "description": "AI-приложение по составлению рациона питания. Собственный домен slimfy.ru, также доступен на 24fox.ru/diet/.",
        "description_en": "AI app for building a diet plan. Own domain slimfy.ru, also available at 24fox.ru/diet/.",
        "stack": ["Python 3", "Flask", "PostgreSQL", "bcrypt"],
        "port": 8085,
        "url": "https://slimfy.ru/",
        "systemd_unit": "diet.service",
        "category": "panel",
    },
    {
        "id": "fox-backend",
        "name": "24fox Backend API",
        "description": "Бэкенд сайта 24fox.ru — авторизация, продажа доступа к VPN, приём платежей, статистика.",
        "description_en": "24fox.ru backend — auth, VPN access sales, payment processing, stats.",
        "stack": ["Python 3", "http.server (stdlib)", "PostgreSQL"],
        "port": 8000,
        "url": None,
        "systemd_unit": "fox-backend.service",
        "category": "panel",
    },
    {
        "id": "glpi-panel",
        "name": "GLPI Panel",
        "description": "Мониторинг корпоративных заявок GLPI (Schlumberger) с Telegram-уведомлениями.",
        "description_en": "Monitoring dashboard for GLPI corporate tickets (Schlumberger) with Telegram alerts.",
        "stack": ["Python 3", "Flask", "PostgreSQL"],
        "port": 8087,
        "url": "/glpi/",
        "systemd_unit": "glpi-panel.service",
        "category": "panel",
    },
    {
        "id": "kkal",
        "name": "KKAL",
        "description": "Трекер калорий и тренировок.",
        "description_en": "Calorie and workout tracker.",
        "stack": ["Python 3", "Flask", "PostgreSQL"],
        "port": 8088,
        "url": "/kkal/",
        "systemd_unit": "kkal.service",
        "category": "panel",
    },
    {
        "id": "social",
        "name": "Social Autoposting",
        "description": "Автопостинг в соцсети (VK, Instagram, Threads, Facebook) по расписанию.",
        "description_en": "Scheduled autoposting to social networks (VK, Instagram, Threads, Facebook).",
        "stack": ["Python 3", "http.server (stdlib)", "JSON-хранилище"],
        "port": 8081,
        "url": "/social/",
        "systemd_unit": "social.service",
        "category": "panel",
    },
    {
        "id": "trade",
        "name": "Trade Panel",
        "description": "Торговля фьючерсами на BingX через приватный REST API (HMAC-подпись запросов): баланс, позиции, ордера.",
        "description_en": "BingX futures trading via private REST API (HMAC-signed requests): balance, positions, orders.",
        "stack": ["Python 3", "Flask", "Gunicorn", "PostgreSQL", "cryptography (Fernet)"],
        "port": 8089,
        "url": "/trade/",
        "systemd_unit": "trade.service",
        "category": "panel",
    },
    {
        "id": "tree",
        "name": "Family Tree",
        "description": "Семейное древо с экспортом в Excel.",
        "description_en": "Family tree with Excel export.",
        "stack": ["Python 3", "http.server (stdlib)", "PostgreSQL", "openpyxl"],
        "port": 8082,
        "url": "/tree/",
        "systemd_unit": "tree.service",
        "category": "panel",
    },
    {
        "id": "train",
        "name": "Train",
        "description": "Статическая обучающая страница, отдаётся напрямую nginx (без бэкенда).",
        "description_en": "Static training page, served directly by nginx (no backend).",
        "stack": ["HTML", "CSS", "JS (статика)"],
        "port": None,
        "url": "/train/",
        "systemd_unit": None,
        "category": "static",
    },
    {
        "id": "photo-backup",
        "name": "Photo/Video Backup",
        "description": "Архив фото и видео, оставшийся от Immich (сам Immich удалён): upload-archive, дамп БД и docker-compose.yml, ~80 ГБ.",
        "description_en": "Photo and video archive left over from Immich (Immich itself removed): upload-archive, DB dump and docker-compose.yml, ~80 GB.",
        "stack": ["Файловый архив", "PostgreSQL dump"],
        "port": None,
        "url": None,
        "systemd_unit": None,
        "category": "static",
    },
    {
        "id": "telega",
        "name": "Telega",
        "description": "Self-hosted веб-клиент Telegram (сборка tweb), отдельный поддомен, раздаётся nginx с проксированием к серверам Telegram.",
        "description_en": "Self-hosted Telegram web client (tweb build), own subdomain, served by nginx with proxying to Telegram servers.",
        "stack": ["tweb", "TypeScript", "nginx (статика + WS-прокси)"],
        "port": None,
        "url": "https://telega.24fox.ru/",
        "systemd_unit": None,
        "category": "static",
    },
    {
        "id": "yadisk-migrate",
        "name": "Yandex → Google Migrate",
        "description": "Фоновое копирование файлов с Яндекс.Диска на Google Drive через rclone (без веб-морды).",
        "description_en": "Background copy of files from Yandex Disk to Google Drive via rclone (no web UI).",
        "stack": ["rclone", "bash"],
        "port": None,
        "url": None,
        "systemd_unit": "yadisk-migrate.service",
        "category": "panel",
    },
    {
        "id": "plan",
        "name": "Plan",
        "description": "Эта панель — карта всех сервисов VPS со стеком и живым статусом.",
        "description_en": "This dashboard — a map of all VPS services with stack and live status.",
        "stack": ["Python 3", "Flask"],
        "port": PORT,
        "url": "/plan/",
        "systemd_unit": "plan.service",
        "category": "panel",
    },
    {
        "id": "free",
        "name": "free",
        "description": "Панель управления VLESS+XHTTP+REALITY (Xray) — создание ключей с подписями и QR-кодом deep-link.",
        "description_en": "VLESS+XHTTP+REALITY (Xray) admin panel — key creation with labels and QR-code deep-link.",
        "stack": ["Python 3", "Flask", "Xray-core"],
        "port": 8086,
        "url": "/free/",
        "systemd_unit": "free.service",
        "category": "panel",
    },
    {
        "id": "xray",
        "name": "Xray-core",
        "description": "VLESS+XHTTP+REALITY сервер (порт 443, делит его с nginx через SNI-роутинг). Слушает только 127.0.0.1:8444, наружу торчит через nginx stream.",
        "description_en": "VLESS+XHTTP+REALITY server (shares port 443 with nginx via SNI routing). Listens only on 127.0.0.1:8444, exposed via nginx stream.",
        "stack": ["Xray-core"],
        "port": None,
        "url": None,
        "systemd_unit": "xray.service",
        "category": "infra",
    },
    {
        "id": "nginx",
        "name": "nginx",
        "description": "Реверс-прокси и веб-сервер для 24fox.ru — маршрутизирует все /xxx/ пути на соответствующие сервисы, терминирует TLS. С 2026-07-20 также содержит stream-блок с SNI-роутингом на 443 (24fox.ru → nginx, addons.mozilla.org → Xray).",
        "description_en": "Reverse proxy and web server for 24fox.ru — routes all /xxx/ paths to the matching services, terminates TLS. Since 2026-07-20 also runs a stream block doing SNI routing on 443 (24fox.ru → nginx, addons.mozilla.org → Xray).",
        "stack": ["nginx-full (stream module)", "Let's Encrypt (certbot)"],
        "port": None,
        "url": None,
        "systemd_unit": "nginx.service",
        "category": "infra",
    },
    {
        "id": "postgresql",
        "name": "PostgreSQL 16",
        "description": "Общая база данных foxdb, используется большинством панелей (awg-panel, diet, glpi-panel, kkal, trade, tree, fox-backend).",
        "description_en": "Shared foxdb database, used by most panels (awg-panel, diet, glpi-panel, kkal, trade, tree, fox-backend).",
        "stack": ["PostgreSQL 16"],
        "port": 5432,
        "url": None,
        "systemd_unit": "postgresql@16-main.service",
        "category": "infra",
    },
    {
        "id": "fail2ban",
        "name": "fail2ban",
        "description": "Защита от брутфорса — банит IP по логам после подозрительной активности.",
        "description_en": "Brute-force protection — bans IPs based on logs after suspicious activity.",
        "stack": ["fail2ban", "iptables"],
        "port": None,
        "url": None,
        "systemd_unit": "fail2ban.service",
        "category": "infra",
    },
]


def live_status(unit: str) -> str:
    try:
        r = subprocess.run(
            ["systemctl", "is-active", unit],
            capture_output=True, text=True, timeout=3,
        )
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def docker_status(container: str) -> str:
    try:
        r = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container],
            capture_output=True, text=True, timeout=3,
        )
        return "active" if r.stdout.strip() == "running" else "inactive"
    except Exception:
        return "unknown"


@app.get("/api/status")
def api_status():
    out = {}
    for svc in SERVICES:
        unit = svc["systemd_unit"]
        if unit:
            out[svc["id"]] = live_status(unit)
        elif svc.get("docker_container"):
            out[svc["id"]] = docker_status(svc["docker_container"])
        else:
            out[svc["id"]] = "static"
    return jsonify(out)


PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan — карта сервисов VPS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* Hallmark · custom dashboard (non-marketing) · tone: technical-dark
 * paper: oklch(16% 0.014 265) · accent: cobalt oklch(62% 0.19 262)
 * display: Space Grotesk · body: Inter · mono: JetBrains Mono
 * statuses: ok=oklch(72% .17 155) bad=oklch(62% .21 25) idle=oklch(66% .16 305) */
:root{
  --color-paper: oklch(16% 0.014 265);
  --color-paper-2: oklch(20% 0.017 264);
  --color-paper-3: oklch(24% 0.02 264);
  --color-border: oklch(29% 0.018 264);
  --color-ink: oklch(94% 0.006 264);
  --color-ink-muted: oklch(68% 0.014 264);
  --color-ink-faint: oklch(50% 0.014 264);
  --color-accent: oklch(62% 0.19 262);
  --color-accent-2: oklch(72% 0.15 262);
  --color-ok: oklch(72% 0.17 155);
  --color-bad: oklch(62% 0.21 25);
  --color-idle: oklch(66% 0.16 305);

  --font-display: "Space Grotesk", ui-sans-serif, system-ui, sans-serif;
  --font-body: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", monospace;

  --space-xs: 4px; --space-sm: 8px; --space-md: 16px; --space-lg: 24px;
  --space-xl: 40px; --space-2xl: 64px;

  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --dur-fast: 140ms; --dur-med: 260ms;
}
*{box-sizing:border-box}
html,body{overflow-x:clip}
body{
  margin:0;font-family:var(--font-body);background:var(--color-paper);color:var(--color-ink);
  background-image:
    radial-gradient(ellipse 900px 500px at 15% -10%, oklch(30% 0.05 262 / 0.35), transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 0%, oklch(28% 0.06 305 / 0.18), transparent 55%);
  background-attachment:fixed;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit}

header{padding:var(--space-2xl) var(--space-xl) var(--space-lg); max-width:1280px; margin:0 auto;}
.eyebrow{font-family:var(--font-mono);font-size:12px;letter-spacing:.08em;color:var(--color-accent-2);
  text-transform:uppercase;margin:0 0 var(--space-sm);}
header h1{margin:0 0 var(--space-sm);font-family:var(--font-display);font-size:clamp(28px,4vw,40px);
  font-weight:700;letter-spacing:-.01em;overflow-wrap:anywhere;min-width:0;}
header p{margin:0 0 var(--space-lg);color:var(--color-ink-muted);font-size:15px;max-width:60ch;}
.credit{font-family:var(--font-mono);font-size:12px;color:var(--color-ink-faint);
  margin:0 0 var(--space-lg);letter-spacing:.01em;}
.credit b{color:var(--color-ink-muted);font-weight:600;}

.stats{display:flex;flex-wrap:wrap;gap:var(--space-md);}
.stat{
  background:var(--color-paper-2);border:1px solid var(--color-border);border-radius:14px;
  padding:14px 20px;min-width:120px;
  opacity:0;transform:translateY(6px);
  animation:rise var(--dur-med) var(--ease-out) forwards;
}
.stat b{display:block;font-family:var(--font-display);font-size:26px;font-weight:700;line-height:1.1;}
.stat span{font-size:12px;color:var(--color-ink-muted);}
.stat.ok b{color:var(--color-ok);}
.stat.bad b{color:var(--color-bad);}
.stat.accent b{color:var(--color-accent-2);}

main{padding:0 var(--space-xl) var(--space-2xl);max-width:1280px;margin:0 auto;}
h2.section{
  font-family:var(--font-mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--color-ink-faint);margin:var(--space-xl) 0 var(--space-md);font-weight:500;
  display:flex;align-items:center;gap:10px;
}
h2.section::after{content:"";flex:1;height:1px;background:var(--color-border);}
h2.section .n{color:var(--color-ink-muted);}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(272px,1fr));gap:14px;}

.card{
  position:relative;background:var(--color-paper-2);border:1px solid var(--color-border);
  border-radius:14px;padding:18px 20px;display:flex;flex-direction:column;gap:10px;
  opacity:0;transform:translateY(10px);
  animation:rise var(--dur-med) var(--ease-out) forwards;
  transition:transform var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out),
    box-shadow var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out);
}
.card:hover{
  transform:translateY(-3px);
  border-color:oklch(45% 0.06 262 / 0.6);
  background:var(--color-paper-3);
  box-shadow:0 12px 28px -12px oklch(10% 0.02 264 / 0.55), 0 0 0 1px oklch(62% 0.19 262 / 0.08);
}
@keyframes rise{to{opacity:1;transform:translateY(0);}}

.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;}
.num{font-family:var(--font-mono);font-size:12px;color:var(--color-accent-2);margin-right:8px;font-weight:500;}
.card-title{font-family:var(--font-display);font-size:16px;font-weight:600;letter-spacing:-.005em;}
.card-title a{text-decoration:none;border-bottom:1px solid transparent;
  transition:border-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out);}
.card-title a:hover{color:var(--color-accent-2);border-color:var(--color-accent-2);}
.card-title a:focus-visible{outline:2px solid var(--color-accent-2);outline-offset:3px;border-radius:3px;}

.badge{
  font-family:var(--font-mono);font-size:11px;padding:3px 9px 3px 7px;border-radius:20px;
  font-weight:500;white-space:nowrap;display:flex;align-items:center;gap:6px;flex-shrink:0;
}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;position:relative;flex-shrink:0;}
.badge.active{color:var(--color-ok);background:oklch(72% 0.17 155 / 0.12);}
.badge.active .dot{background:var(--color-ok);}
.badge.active .dot::after{
  content:"";position:absolute;inset:-4px;border-radius:50%;border:1.5px solid var(--color-ok);
  animation:pulse 2.2s var(--ease-in-out) infinite;
}
.badge.inactive,.badge.failed{color:var(--color-bad);background:oklch(62% 0.21 25 / 0.12);}
.badge.inactive .dot,.badge.failed .dot{background:var(--color-bad);}
.badge.static{color:var(--color-ink-muted);background:oklch(68% 0.014 264 / 0.1);}
.badge.static .dot{background:var(--color-ink-faint);}
.badge.unknown{color:var(--color-idle);background:oklch(66% 0.16 305 / 0.12);}
.badge.unknown .dot{background:var(--color-idle);}
@keyframes pulse{0%{transform:scale(0.6);opacity:.9;}100%{transform:scale(1.8);opacity:0;}}

.desc{font-size:13px;color:var(--color-ink-muted);line-height:1.55;}
.desc-en{font-size:12px;color:var(--color-ink-faint);line-height:1.5;font-style:italic;}
.meta{font-family:var(--font-mono);font-size:11.5px;color:var(--color-ink-faint);}
.stack{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px;}
.tag{
  font-family:var(--font-mono);font-size:11px;background:var(--color-paper-3);
  border:1px solid var(--color-border);color:var(--color-ink-muted);padding:3px 8px;border-radius:6px;
}

footer{max-width:1280px;margin:0 auto;padding:0 var(--space-xl) var(--space-2xl);
  color:var(--color-ink-faint);font-size:12px;font-family:var(--font-mono);}

@media (max-width:520px){
  header,main,footer{padding-left:var(--space-md);padding-right:var(--space-md);}
}
@media (prefers-reduced-motion: reduce){
  .stat,.card{animation:none;opacity:1;transform:none;}
  .card{transition:none;}
  .card:hover{transform:none;}
  .badge.active .dot::after{animation:none;display:none;}
}
</style>
</head>
<body>
<header>
  <p class="eyebrow">24fox.ru · VPS</p>
  <h1>Карта сервисов</h1>
  <p>Всё, что крутится на этом сервере — стек, порт и живой статус каждого компонента.</p>
  <p class="credit">Designed &amp; built by <b>Egor Kuznetsov</b></p>
  <div class="stats" id="stats"></div>
</header>
<main>
  <h2 class="section">Панели <span class="n" id="count-panel"></span></h2>
  <div class="grid" id="grid-panel"></div>
  <h2 class="section">Инфраструктура <span class="n" id="count-infra"></span></h2>
  <div class="grid" id="grid-infra"></div>
  <h2 class="section">Статика <span class="n" id="count-static"></span></h2>
  <div class="grid" id="grid-static"></div>
</main>
<footer>обновляется каждые 15с · systemctl is-active</footer>
<script>
const SERVICES = __SERVICES_JSON__;

function statusLabel(s){
  return {active:"работает", inactive:"остановлен", failed:"ошибка",
          static:"статика", unknown:"нет данных"}[s] || s;
}

function renderStats(statuses){
  const total = SERVICES.length;
  const ok = SERVICES.filter(s => statuses[s.id] === 'active').length;
  const bad = SERVICES.filter(s => ['inactive','failed'].includes(statuses[s.id])).length;
  const el = document.getElementById('stats');
  el.innerHTML = `
    <div class="stat accent" style="animation-delay:0ms"><b>${total}</b><span>всего сервисов</span></div>
    <div class="stat ok" style="animation-delay:60ms"><b>${ok}</b><span>работает</span></div>
    <div class="stat ${bad ? 'bad' : ''}" style="animation-delay:120ms"><b>${bad}</b><span>требуют внимания</span></div>
  `;
}

function render(statuses){
  const grids = {panel: document.getElementById('grid-panel'),
                 infra: document.getElementById('grid-infra'),
                 static: document.getElementById('grid-static')};
  Object.values(grids).forEach(g => g.innerHTML = '');

  const counts = {panel:0, infra:0, static:0};
  SERVICES.forEach(s => counts[s.category]++);
  document.getElementById('count-panel').textContent = counts.panel;
  document.getElementById('count-infra').textContent = counts.infra;
  document.getElementById('count-static').textContent = counts.static;

  const order = ['panel','infra','static'];
  const sorted = order.flatMap(c => SERVICES.filter(s => s.category === c));
  let i = 0;
  for(const svc of sorted){
    const st = statuses[svc.id] || 'unknown';
    const card = document.createElement('div');
    card.className = 'card';
    card.style.animationDelay = `${Math.min(i, 10) * 35}ms`;
    i++;

    const titleHtml = svc.url
      ? `<a href="${svc.url}" target="_blank" rel="noopener">${svc.name}</a>`
      : svc.name;

    const portMeta = svc.port ? `:${svc.port}` : '';
    const unitMeta = svc.systemd_unit ? svc.systemd_unit : '';
    const meta = [portMeta, unitMeta].filter(Boolean).join('  ·  ');

    card.innerHTML = `
      <div class="card-head">
        <div class="card-title"><span class="num">${String(i).padStart(2,'0')}</span>${titleHtml}</div>
        <span class="badge ${st}"><span class="dot"></span>${statusLabel(st)}</span>
      </div>
      <div class="desc">${svc.description}</div>
      <div class="desc-en">${svc.description_en}</div>
      <div class="stack">${svc.stack.map(t => `<span class="tag">${t}</span>`).join('')}</div>
      ${meta ? `<div class="meta">${meta}</div>` : ''}
    `;
    grids[svc.category].appendChild(card);
  }
  renderStats(statuses);
}

async function tick(){
  try{
    const r = await fetch('api/status');
    if(!r.ok) throw new Error(r.status);
    const statuses = await r.json();
    render(statuses);
  }catch(e){
    render({});
  }
}
tick();
setInterval(tick, 15000);
</script>
</body>
</html>
"""


@app.get("/")
def index():
    import json as _json
    services_json = _json.dumps(SERVICES, ensure_ascii=False)
    return PAGE.replace("__SERVICES_JSON__", services_json)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT)
