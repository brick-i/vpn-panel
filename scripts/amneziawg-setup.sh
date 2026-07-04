#!/bin/bash
set -e

echo "⚡ AmneziaWG Server Setup"
echo "========================="

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash amneziawg-setup.sh"
  exit 1
fi

PORT=${1:-51820}
DNS=${2:-"1.1.1.1, 8.8.8.8"}

echo "[1/4] Installing AmneziaWG..."
apt-get update -y
apt-get install -y curl ca-certificates gnupg lsb-release qrencode

# Add AmneziaWG repo
curl -fsSL https://deb.debian.org/debian/pool/main/a/amneziawg/amneziawg.gpg.key | gpg --dearmor -o /usr/share/keyrings/amneziawg.gpg
echo "deb [signed-by=/usr/share/keyrings/amneziawg.gpg] https://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/amneziawg.list
apt-get update -y
apt-get install -y amneziawg

echo "[2/4] Generating server keys..."
SERVER_PRIVKEY=$(wg genkey)
SERVER_PUBKEY=$(echo "$SERVER_PRIVKEY" | wg pubkey)

echo "[3/4] Creating interface config..."
mkdir -p /etc/wireguard

cat > /etc/wireguard/awg0.conf << EOF
[Interface]
Address = 10.0.0.1/24
ListenPort = $PORT
PrivateKey = $SERVER_PRIVKEY
DNS = $DNS
EOF

echo "[4/4] Starting AmneziaWG..."
awg-quick up awg0

# Enable on boot
systemctl enable awg-quick@awg0 2>/dev/null || true

echo ""
echo "========================="
echo "✅ AmneziaWG configured!"
echo ""
echo "Server Public Key: $SERVER_PUBKEY"
echo "Listen Port: $PORT"
echo "Interface: awg0"
echo "========================="
