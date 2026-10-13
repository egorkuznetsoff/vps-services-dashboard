# vps-services-dashboard

**Plan** — дашборд-карта всех сервисов VPS. Для каждого сервиса показывает номер, название, описание (RU/EN), стек, порт, systemd-юнит и **текущий статус**: панель сама опрашивает `systemctl is-active` каждые 15 секунд.

Продакшен: главная [24fox.ru](https://24fox.ru) и `24fox.ru/plan/`.

## Стек

| Слой | Технология |
|---|---|
| Бэкенд | Python 3, Flask (порт 8083), один файл `app.py` |
| Статусы | `systemctl is-active` (без sudo), `docker inspect` для контейнеров |
| Фронтенд | Vanilla JS + CSS, встроены в `app.py`; шрифты Space Grotesk, Inter, JetBrains Mono |

## Как добавить сервис

Добавьте объект в список `SERVICES` в `app.py`:

```python
{
    "id": "myapp", "name": "My App",
    "description": "…", "description_en": "…",
    "stack": ["Python 3", "Flask"],
    "port": 8090, "url": "/myapp/",
    "systemd_unit": "myapp.service",   # или None для статики
    "category": "panel",               # panel | infra | static
},
```

Номер на карточке присвоится автоматически.

## Развёртывание

1. Зависимости:
   ```bash
   sudo apt install python3-flask
   ```
2. Клон:
   ```bash
   git clone https://github.com/egorkuznetsoff/vps-services-dashboard.git /home/egor/plan
   ```
3. systemd (`/etc/systemd/system/plan.service`):
   ```ini
   [Unit]
   Description=Plan — VPS services map
   After=network.target

   [Service]
   User=egor
   WorkingDirectory=/home/egor/plan
   ExecStart=/usr/bin/python3 /home/egor/plan/app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl daemon-reload && sudo systemctl enable --now plan
   ```
4. nginx — на корень сайта и/или в подпапку:
   ```nginx
   location / { proxy_pass http://127.0.0.1:8083/; }
   location ^~ /plan/ { proxy_pass http://127.0.0.1:8083/; }
   ```

> Авторизации нет: страница показывает внутреннюю архитектуру сервера (порты, юниты). Решение осознанное.

## Автор

**Егор Кузнецов** (Egor Kuznetsov) — идея, разработка, деплой и сопровождение.
GitHub: [@egorkuznetsoff](https://github.com/egorkuznetsoff) · 2026

Часть кода написана в паре с AI-ассистентом Claude (Anthropic).
Репозиторий приватный, все права защищены.
