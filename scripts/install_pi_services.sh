#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BMO_USER="${SUDO_USER:-$USER}"
BACKUP_DIR="${BMO_BACKUP_DIR:-$PROJECT_DIR/../bmo_fridge_backups}"
SYSTEMD_DIR="$PROJECT_DIR/deploy/systemd"

if [[ ! -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  echo "Missing $PROJECT_DIR/.venv/bin/python"
  echo "Create the virtual environment and install requirements first."
  exit 1
fi

render_unit() {
  local source_file="$1"
  local destination_file="$2"
  sed \
    -e "s|@PROJECT_DIR@|$PROJECT_DIR|g" \
    -e "s|@BMO_USER@|$BMO_USER|g" \
    -e "s|@BACKUP_DIR@|$BACKUP_DIR|g" \
    "$source_file" | sudo tee "$destination_file" >/dev/null
}

render_unit "$SYSTEMD_DIR/bmo-fridge-monitor.service.in" /etc/systemd/system/bmo-fridge-monitor.service
render_unit "$SYSTEMD_DIR/bmo-fridge-web.service.in" /etc/systemd/system/bmo-fridge-web.service
render_unit "$SYSTEMD_DIR/bmo-fridge-backup.service.in" /etc/systemd/system/bmo-fridge-backup.service
sudo install -m 0644 "$SYSTEMD_DIR/bmo-fridge-backup.timer" /etc/systemd/system/bmo-fridge-backup.timer

if [[ ! -f /etc/default/bmo-fridge ]]; then
  printf 'BMO_WEB_HOST=0.0.0.0\nBMO_WEB_PORT=5000\n' | sudo tee /etc/default/bmo-fridge >/dev/null
fi

mkdir -p "$BACKUP_DIR"
sudo systemctl daemon-reload
sudo systemctl enable --now bmo-fridge-monitor.service bmo-fridge-web.service bmo-fridge-backup.timer

for _ in {1..20}; do
  [[ -f "$PROJECT_DIR/fridge.db" ]] && break
  sleep 0.5
done
if [[ -f "$PROJECT_DIR/fridge.db" ]]; then
  sudo systemctl start bmo-fridge-backup.service
else
  echo "Warning: fridge.db was not ready, so the first backup will run on the daily timer."
fi

echo
echo "BMO services installed."
echo "Web app: http://$(hostname -I | awk '{print $1}'):5000"
echo "Backups: $BACKUP_DIR"
echo "Check: sudo systemctl status bmo-fridge-web bmo-fridge-monitor bmo-fridge-backup.timer"
