# VPN Panel

Панель управления VPN сервисами с поддержкой нескольких протоколов. Автоматически генерирует конфигурации для Xray, Hysteria2 и Caddy. Панель скрыта от публичного доступа — доступна только через SSH tunnel.

## Возможности

- 🔐 **Протоколы**: VLESS TCP Reality, VLESS xHTTP Reality, Hysteria2, NaiveProxy
- 👥 **Клиенты**: управление пользователями и их credentials (UUID, пароли)
- 📋 **Подписки**: гибкое назначение инбаундов клиентам, ссылки для импорта в VPN клиент
- 🌐 **Домены**: управление доменами для SNI маскировки
- ⚙️ **Авто-конфигурация**: автоматическая генерация конфигов при любом изменении
- 🐳 **Docker**: все сервисы в контейнерах
- 🛡️ **Безопасность**: панель доступна только через SSH tunnel, публичный домен показывает сайт-заглушку

## Стек

| Компонент | Технология |
|-----------|------------|
| Backend | FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database | SQLite (aiosqlite) |
| Auth | JWT (python-jose) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| VPN | Xray-core, Hysteria2, Caddy (NaiveProxy) |
| Proxy / SSL | Caddy (автоматический Let's Encrypt) |
| Package manager | uv |

## Архитектура

```
┌─────────────────────────────────────────────┐
│                   VPS                        │
│                                              │
│  Internet ──► Caddy :443                     │
│                 │                            │
│                 ├── /sub/*  ──► FastAPI       │  (публично)
│                 └── /*      ──► заглушка      │  (публично)
│                                              │
│  SSH Tunnel ──► Caddy :8080                  │
│                 │                            │
│                 ├── /api/*  ──► FastAPI       │  (только SSH)
│                 └── /*      ──► Frontend      │  (только SSH)
│                                              │
│  Xray      :random  (VLESS Reality)          │
│  Hysteria2 :443     (UDP)                    │
│  Caddy     :443     (NaiveProxy)             │
└─────────────────────────────────────────────┘
```

## Установка на VPS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kiryarah87/vpnpanel/main/install.sh)
```

Скрипт автоматически:
1. Обновит систему (`apt update && apt upgrade`)
2. Настроит SSH ключи и отключит вход по паролю
3. Установит и настроит UFW — закроет все порты кроме необходимых
4. Установит и настроит fail2ban — защита SSH от брутфорса
5. Установит Docker
6. Запросит домен и данные администратора
7. Соберёт и запустит все контейнеры

### Требования к серверу

- Ubuntu 22.04 / Debian 12
- Минимум 1 GB RAM
- Домен с A-записью, указывающей на IP сервера
- Открытые порты: `22`, `443` (tcp/udp), `10000-60000` (tcp/udp)

### Доступ к панели после установки

Панель **не доступна публично**. Подключение только через SSH tunnel:

```bash
ssh -L 8080:127.0.0.1:8080 user@ВАШ_IP
```

Затем откройте в браузере: `http://localhost:8080`

## Локальная разработка

### Требования

- Python 3.12+
- Node.js 20+
- uv

### Запуск бэкенда

```bash
git clone https://github.com/kiryarah87/vpnpanel.git
cd vpnpanel

cp .env.example .env

uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

### Запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

### Запуск через Docker (локально)

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Панель: `http://localhost`
API docs: `http://localhost:8000/docs`

## Переменные окружения

### `.env` (бэкенд)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `APP_NAME` | Название приложения | `VPN Panel` |
| `DEBUG` | Режим отладки | `false` |
| `HOST` | Хост бэкенда | `127.0.0.1` |
| `PORT` | Порт бэкенда | `8000` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///./vpnpanel.db` |
| `SECRET_KEY` | Секретный ключ JWT | — |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `JWT_EXPIRE_MINUTES` | Время жизни токена | `1440` |
| `ADMIN_USERNAME` | Логин администратора | `admin` |
| `ADMIN_PASSWORD` | Пароль администратора | — |
| `DOMAIN` | Публичный домен сервера | `localhost` |
| `SUBSCRIPTION_BASE_URL` | Базовый URL для подписок | `http://localhost:8000` |

### `frontend/.env` (фронтенд)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VITE_API_URL` | URL бэкенда (пусто = тот же домен) | `` |

## Структура проекта

```
vpnpanel/
├── app/
│   ├── api/v1/              # API эндпоинты
│   ├── config_gen/          # Генерация конфигов
│   │   └── configs/
│   │       ├── caddy/
│   │       │   └── decoy/
│   │       │       └── index.html   # Сайт-заглушка
│   │       ├── xray/
│   │       └── hysteria2/
│   ├── core/                # Настройки, БД, зависимости
│   ├── models/              # SQLAlchemy модели
│   ├── repositories/        # Слой доступа к данным
│   ├── schemas/             # Pydantic схемы
│   └── services/            # Бизнес-логика
├── docker/
│   ├── caddy/
│   ├── hysteria2/
│   └── xray/
├── frontend/                # React приложение
├── migrations/              # Alembic миграции
├── install.sh               # Скрипт установки на VPS
├── .env.example
└── README.md
```

## Поддерживаемые протоколы

| Протокол | Транспорт | Безопасность | Порт |
|----------|-----------|--------------|------|
| VLESS | TCP | Reality | случайный |
| VLESS | xHTTP | Reality | случайный |
| Hysteria2 | UDP | TLS (Let's Encrypt) | 443 |
| NaiveProxy | HTTPS | TLS (Let's Encrypt) | 443 |

## Безопасность

- Панель управления доступна **только через SSH tunnel**
- Публичный домен показывает безобидный сайт-заглушку
- SSH вход по паролю отключён (только ключи)
- UFW блокирует все порты кроме `22`, `443`, `10000-60000`
- fail2ban: бан после 3 неудачных попыток SSH на 24 часа
- JWT токены для аутентификации в API
