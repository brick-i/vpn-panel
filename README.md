# AmneziaWG Panel

Web-based management panel for AmneziaVPN (AmneziaWG) servers.

## Features

- **One-click installation** of AmneziaWG on Ubuntu/Debian
- **Client management** — create, edit, delete VPN peers
- **QR codes & config export** — for mobile and desktop clients
- **Real-time monitoring** — connected clients, traffic, system resources
- **Obfuscation settings** — configure Jc, Jmin, Jmax, S1, S2, H1-H4
- **Dark theme** UI

## Quick Install (on server)

```bash
git clone <repo> && cd vpn-panel
sudo bash scripts/install.sh
```

## Manual Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Server starts on `http://localhost:8000`

### Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Dev server on `http://localhost:5173` (proxies API to :8000)

### Production Build

```bash
cd frontend
npm run build
```

Copy `frontend/dist/*` to a static file server or serve from FastAPI.

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | random | JWT signing key |
| `DATABASE_URL` | sqlite | Database connection |

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / SQLite
- **Frontend**: Svelte 5 / Tailwind CSS / Vite
- **VPN**: AmneziaWG (amneziawg-tools)
- **Target OS**: Ubuntu 22.04 / 24.04 LTS

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| GET | `/api/server/status` | Server status |
| POST | `/api/server/start` | Start VPN |
| POST | `/api/server/stop` | Stop VPN |
| GET | `/api/clients` | List clients |
| POST | `/api/clients` | Create client |
| GET | `/api/clients/:id/config` | Download config |
| GET | `/api/stats/overview` | Dashboard stats |

## License

MIT
