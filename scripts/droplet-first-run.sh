#!/bin/bash
# One time, in Termius, on the droplet, as root.
# Do not run this from Windows.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl git ufw

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

mkdir -p /opt
if [ ! -d /opt/self-hosted-ai-starter-kit/.git ]; then
  git clone https://github.com/FehminTaghizada/fehmin8n.git /opt/self-hosted-ai-starter-kit
fi

cd /opt/self-hosted-ai-starter-kit
git pull origin main

if [ ! -f .env ]; then
  cp .env.example .env
fi

IP="$(curl -4 -fsS --max-time 10 https://ifconfig.me || true)"
if [ -z "${IP}" ]; then
  IP="$(hostname -I | awk '{print $1}')"
fi

set_env() {
  key="$1"
  value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
    printf '%s=%s\n' "${key}" "${value}" >> .env
  fi
}

set_env N8N_HOST "${IP}"
set_env N8N_PORT "5678"
set_env N8N_PROTOCOL "http"
set_env N8N_EDITOR_BASE_URL "http://${IP}:5678"
set_env WEBHOOK_URL "http://${IP}:5678/"
set_env N8N_WEBHOOK_URL "http://${IP}:5678/"
set_env N8N_SECURE_COOKIE "false"

docker compose up -d --build
docker compose ps

ufw allow 22/tcp
ufw allow 5678/tcp
ufw allow 8000/tcp
ufw --force enable

curl -fsS "http://127.0.0.1:8000/health"
echo
echo "n8n:    http://${IP}:5678"
echo "health: http://${IP}:8000/health"
