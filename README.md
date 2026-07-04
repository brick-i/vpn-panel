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

## Лицензия

MIT
