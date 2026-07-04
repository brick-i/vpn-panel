# AmneziaWG Panel

Веб-панель управления серверами AmneziaVPN (AmneziaWG).

## Возможности

- **Однострочная установка** AmneziaWG на Ubuntu/Debian
- **Управление клиентами** — создание, редактирование, удаление пиров
- **QR-коды и экспорт конфигов** — для мобильных и десктопных клиентов
- **Мониторинг в реальном времени** — подключённые клиенты, трафик, ресурсы системы
- **Настройки обфускации** — параметры Jc, Jmin, Jmax, S1, S2, H1-H4
- **Тёмная тема** интерфейс

## Быстрая установка (на сервер)

```bash
git clone https://github.com/brick-i/vpn-panel.git && cd vpn-panel
sudo bash scripts/install.sh
```

После установки панель доступна по адресу: `http://ваш-сервер:8000`

## Ручная установка

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Сервер запускается на `http://localhost:8000`

### Frontend (для разработки)

```bash
cd frontend
npm install
npm run dev
```

Dev-сервер на `http://localhost:5173` (проксирует API на :8000)

### Сборка для продакшена

```bash
cd frontend
npm run build
```

Скопируйте содержимое `frontend/dist/*` на статический веб-сервер или раздайте через FastAPI.

## Конфигурация

Переменные окружения:

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `SECRET_KEY` | случайный | Ключ для подписи JWT-токенов |
| `DATABASE_URL` | sqlite | Строка подключения к базе данных |

## Стек технологий

- **Backend**: Python 3.11+ / FastAPI / SQLite
- **Frontend**: Svelte 5 / Tailwind CSS / Vite
- **VPN**: AmneziaWG (amneziawg-tools)
- **Целевая ОС**: Ubuntu 22.04 / 24.04 LTS

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/auth/login` | Авторизация |
| GET | `/api/auth/setup-status` | Проверка наличия админа |
| POST | `/api/auth/setup` | Создание первого админа |
| GET | `/api/server/status` | Статус сервера |
| POST | `/api/server/start` | Запуск VPN |
| POST | `/api/server/stop` | Остановка VPN |
| POST | `/api/server/restart` | Рестарт VPN |
| GET | `/api/server/config` | Получение конфигурации |
| PUT | `/api/server/config` | Обновление конфигурации |
| POST | `/api/server/install` | Установка AmneziaWG |
| GET | `/api/server/install/progress` | Прогресс установки |
| GET | `/api/clients` | Список клиентов |
| POST | `/api/clients` | Создать клиента |
| GET | `/api/clients/:id` | Данные клиента |
| PUT | `/api/clients/:id` | Обновить клиента |
| DELETE | `/api/clients/:id` | Удалить клиента |
| GET | `/api/clients/:id/config` | Скачать .conf файл |
| GET | `/api/stats/overview` | Общая статистика |
| GET | `/api/stats/traffic` | Статистика трафика |
| GET | `/api/stats/clients` | Статистика по клиентам |
| GET | `/api/stats/system` | Информация о системе |

## Структура проекта

```
vpn-panel/
├── backend/
│   ├── main.py              # Точка входа FastAPI
│   ├── config.py            # Настройки
│   ├── database.py          # SQLite (async)
│   ├── models.py            # Pydantic модели
│   ├── routers/
│   │   ├── auth.py          # JWT авторизация
│   │   ├── server.py        # Управление сервером
│   │   ├── clients.py       # CRUD клиентов
│   │   └── stats.py         # Статистика
│   └── services/
│       ├── vpn.py           # Обёртка над awg/wg
│       ├── system.py        # CPU/RAM/disk
│       └── installer.py     # Установщик
├── frontend/
│   └── src/
│       ├── components/      # Svelte компоненты
│       ├── pages/           # Страницы
│       └── lib/             # API клиент, stores
├── scripts/
│   ├── install.sh           # Установка панели
│   └── amneziawg-setup.sh   # Установка AmneziaWG
└── README.md
```

## Решение проблем

### Ошибка сборки pydantic-core на Python 3.14

**Симптом:**
```
error: the configured Python interpreter version (3.14) is newer than PyO3's maximum supported version (3.13)
ERROR: Failed building wheel for pydantic-core
```

**Причина:** Библиотека `pydantic-core` использует PyO3 для связки с Rust. Текущая версия PyO3 (0.22.2) поддерживает только Python до 3.13 включительно. Python 3.14 ещё не поддерживается.

**Решение — установить Python 3.13:**

```bash
# Debian/Ubuntu
apt-get install -y python3.13 python3.13-venv

# Пересоздать venv
cd /opt/vpn-panel/backend
rm -rf venv
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Перезапустить сервис
systemctl restart vpn-panel
```

**Альтернатива (не рекомендуется):** установить переменную окружения перед `pip install`:
```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install -r requirements.txt
```
Этот флаг заставляет PyO3 собираться через стабильный ABI, но может работать нестабильно.

### AmneziaWG не устанавливается

**Симптом:** ошибка на шаге установки AmneziaWG.

**Решение — ручная установка:**
```bash
# Добавить репозиторий
curl -fsSL https://deb.debian.org/debian/pool/main/a/amneziawg/amneziawg.gpg.key | gpg --dearmor -o /usr/share/keyrings/amneziawg.gpg
echo "deb [signed-by=/usr/share/keyrings/amneziawg.gpg] https://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/amneziawg.list

# Установить
apt-get update -y
apt-get install -y amneziawg

# Проверить
awg --version
```

### Панель не запускается

**Проверьте статус:**
```bash
systemctl status vpn-panel
journalctl -u vpn-panel -f
```

**Перезапустите:**
```bash
systemctl restart vpn-panel
```

**Проверьте порт:**
```bash
ss -tlnp | grep 8000
```

### Клиент не может подключиться

1. Убедитесь, что AmneziaWG запущен: `awg show awg0`
2. Проверьте firewall: `ufw allow 51820/udp`
3. Проверьте, что в конфиге клиента правильный `Endpoint` (IP сервера и порт)
4. Убедитесь, что `AllowedIPs` на сервере включает IP клиента

## Лицензия

MIT
