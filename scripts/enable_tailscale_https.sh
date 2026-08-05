#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale is not installed. Follow https://tailscale.com/download/linux first."
  exit 1
fi

if ! sudo tailscale status >/dev/null 2>&1; then
  echo "This Pi is not connected to Tailscale. Run: sudo tailscale up"
  exit 1
fi

sudo sed -i 's/^BMO_WEB_HOST=.*/BMO_WEB_HOST=127.0.0.1/' /etc/default/bmo-fridge
sudo systemctl restart bmo-fridge-web.service
sudo tailscale serve --bg 5000

echo
echo "Private HTTPS is enabled. Install Tailscale on the phone and sign into the same account."
sudo tailscale serve status
