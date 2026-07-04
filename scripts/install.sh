#!/bin/bash
set -e

echo "⚡ AmneziaWG Panel - Quick Install"
echo "================================="

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash install.sh"
  exit 1
fi

# Check OS
if ! grep -q "Debian\|Ubuntu" /etc/os-release 2>/dev/null; then
  echo "This script is designed for Debian/Ubuntu"
  exit 1
fi

echo "[1/5] Updating system..."
apt-get update -y
apt-get install -y software-properties-common curl git

echo "Installing Python 3.13..."
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update -y
apt-get install -y python3.13 python3.13-venv python3.13-dev

echo "[2/5] Installing AmneziaWG..."
bash <(curl -fsSL https://raw.githubusercontent.com/amnezia-vpn/amnezia-client/main/client/scripts/install.sh) 2>/dev/null || {
  echo "AmneziaWG installation from script failed. Trying manual install..."
  curl -fsSL https://deb.debian.org/debian/pool/main/a/amneziawg/amneziawg.gpg.key | gpg --dearmor -o /usr/share/keyrings/amneziawg.gpg
  echo "deb [signed-by=/usr/share/keyrings/amneziawg.gpg] https://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/amneziawg.list
  apt-get update -y
  apt-get install -y amneziawg
}

mkdir -p /etc/wireguard

echo "[3/5] Setting up VPN Panel..."
PANEL_DIR="/opt/vpn-panel"
mkdir -p "$PANEL_DIR"
cp -r ./* "$PANEL_DIR/"

cd "$PANEL_DIR/backend"
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "[4/5] Creating systemd service..."
cat > /etc/systemd/system/vpn-panel.service << 'EOF'
[Unit]
Description=AmneziaWG VPN Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-panel/backend
ExecStart=/opt/vpn-panel/backend/venv/bin/python main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "[5/5] Starting service..."
systemctl daemon-reload
systemctl enable vpn-panel
systemctl start vpn-panel

echo ""
echo "================================="
echo "✅ AmneziaWG Panel installed!"
echo ""
echo "🌐 Open: http://$(curl -s ifconfig.me):8000"
echo ""
echo "Commands:"
echo "  systemctl status vpn-panel"
echo "  systemctl restart vpn-panel"
echo "  journalctl -u vpn-panel -f"
echo "================================="
