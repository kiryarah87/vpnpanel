#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}"
echo "=============================="
echo "     VPN Panel Installer      "
echo "=============================="
echo -e "${NC}"

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Запустите скрипт от root: sudo bash install.sh${NC}"
    exit 1
fi

# ==============================
# 1. Обновление системы
# ==============================
echo -e "${YELLOW}Обновление системы...${NC}"
apt-get update -y && apt-get upgrade -y
apt-get install -y curl git openssl ufw fail2ban

# ==============================
# 2. Настройка SSH ключей
# ==============================
echo ""
echo -e "${GREEN}=== Настройка SSH ===${NC}"
echo ""

SSH_USER=${SUDO_USER:-root}
SSH_HOME=$(eval echo "~$SSH_USER")

if [ ! -f "$SSH_HOME/.ssh/authorized_keys" ] || [ ! -s "$SSH_HOME/.ssh/authorized_keys" ]; then
    echo -e "${YELLOW}SSH ключи не найдены.${NC}"
    echo "1) Сгенерировать новую пару ключей на сервере"
    echo "2) Вставить свой публичный ключ вручную"
    read -p "Выберите [1/2]: " SSH_CHOICE

    mkdir -p "$SSH_HOME/.ssh"
    chmod 700 "$SSH_HOME/.ssh"

    if [ "$SSH_CHOICE" = "1" ]; then
        ssh-keygen -t ed25519 -f "$SSH_HOME/.ssh/vpnpanel_key" -N "" -C "vpnpanel"
        cat "$SSH_HOME/.ssh/vpnpanel_key.pub" >> "$SSH_HOME/.ssh/authorized_keys"
        chmod 600 "$SSH_HOME/.ssh/authorized_keys"
        chown -R "$SSH_USER:$SSH_USER" "$SSH_HOME/.ssh"
        echo ""
        echo -e "${RED}ВАЖНО: Скопируйте приватный ключ и сохраните на своём компьютере:${NC}"
        echo ""
        cat "$SSH_HOME/.ssh/vpnpanel_key"
        echo ""
    else
        read -p "Вставьте ваш публичный ключ: " PUBLIC_KEY
        echo "$PUBLIC_KEY" >> "$SSH_HOME/.ssh/authorized_keys"
        chmod 600 "$SSH_HOME/.ssh/authorized_keys"
        chown -R "$SSH_USER:$SSH_USER" "$SSH_HOME/.ssh"
        echo -e "${GREEN}Публичный ключ добавлен!${NC}"
    fi
else
    echo -e "${GREEN}SSH ключи уже настроены.${NC}"
fi

read -p "Отключить вход по паролю SSH (только ключи)? [y/N]: " DISABLE_PASS
if [[ "$DISABLE_PASS" =~ ^[Yy]$ ]]; then
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    systemctl restart sshd
    echo -e "${GREEN}Вход по паролю отключён!${NC}"
    echo -e "${RED}Убедитесь что SSH ключ работает перед закрытием сессии!${NC}"
fi

# ==============================
# 3. Настройка UFW
# ==============================
echo ""
echo -e "${GREEN}=== Настройка фаервола (UFW) ===${NC}"
echo ""

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    comment 'SSH'
ufw allow 443/tcp   comment 'HTTPS'
ufw allow 443/udp   comment 'Hysteria2'
ufw allow 10000:60000/tcp comment 'VPN TCP'
ufw allow 10000:60000/udp comment 'VPN UDP'
ufw --force enable

echo -e "${GREEN}Фаервол настроен!${NC}"
ufw status numbered

# ==============================
# 4. Настройка fail2ban
# ==============================
echo ""
echo -e "${GREEN}=== Настройка fail2ban ===${NC}"

cat > /etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8

[sshd]
enabled  = true
port     = ssh
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
maxretry = 3
bantime  = 86400
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo -e "${GREEN}fail2ban настроен!${NC}"

# ==============================
# 5. Настройка панели
# ==============================
echo ""
echo -e "${GREEN}=== Настройка панели ===${NC}"
echo ""

read -p "Введите домен (например: vpn.example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Домен обязателен!${NC}"
    exit 1
fi

read -p "Имя администратора [admin]: " ADMIN_USERNAME
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}

while true; do
    read -s -p "Пароль администратора: " ADMIN_PASSWORD
    echo ""
    read -s -p "Повторите пароль: " ADMIN_PASSWORD2
    echo ""
    if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD2" ]; then
        break
    fi
    echo -e "${RED}Пароли не совпадают!${NC}"
done

# Клонирование репозитория
INSTALL_DIR="/opt/vpnpanel"
echo ""
echo -e "${YELLOW}Клонирование репозитория в ${INSTALL_DIR}...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Директория уже существует, обновляем...${NC}"
    git -C "$INSTALL_DIR" pull
else
    git clone https://github.com/kiryarah87/vpnpanel.git "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

PANEL_PORT=8080
SECRET_KEY=$(openssl rand -hex 32)

cat > .env <<EOF
APP_NAME="VPN Panel"
DEBUG=false
HOST=127.0.0.1
PORT=${PANEL_PORT}

DATABASE_URL="sqlite+aiosqlite:///./vpnpanel.db"

SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

ADMIN_USERNAME=${ADMIN_USERNAME}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

DOCKER_SOCKET=unix:///var/run/docker.sock
VPN_NETWORK=vpnpanel_network
MAX_INBOUNDS_PER_SUBSCRIPTION=10

DOMAIN=${DOMAIN}
SUBSCRIPTION_BASE_URL="https://${DOMAIN}"
EOF

# Предгенерируем Caddyfile для VPS
# Предгенерируем Caddyfile для VPS
mkdir -p app/config_gen/configs/caddy
mkdir -p app/config_gen/configs/certs
mkdir -p app/config_gen/configs/xray
mkdir -p app/config_gen/configs/hysteria2

cat > app/config_gen/configs/caddy/Caddyfile <<EOF
${DOMAIN} {
    reverse_proxy /sub/* localhost:8000

    root * /srv/decoy
    file_server
}

http://localhost:${PANEL_PORT} {
    root * /srv/frontend

    reverse_proxy /api/* localhost:8000

    try_files {path} /index.html
    file_server
}
EOF

cat > frontend/.env <<EOF
VITE_API_URL=
EOF

echo -e "${GREEN}.env создан!${NC}"

# Создать файл БД чтобы Docker не создал директорию
touch vpnpanel.db

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Установка Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

echo ""
echo -e "${YELLOW}Сборка и запуск контейнеров...${NC}"
docker compose -f docker/docker-compose.yml up -d --build

echo -e "${YELLOW}Ожидание запуска...${NC}"
sleep 5
docker logs vpnpanel --tail 10

echo ""
echo -e "${GREEN}=============================="
echo " Установка завершена!"
echo "=============================="
echo -e "${NC}"
echo -e "Публичный сайт: ${GREEN}https://${DOMAIN}${NC} (заглушка)"
echo ""
echo -e "${YELLOW}Доступ к панели — только через SSH tunnel:${NC}"
echo -e "  ${BLUE}ssh -L 8080:127.0.0.1:${PANEL_PORT} ${SSH_USER}@ВАШ_IP${NC}"
echo -e "  Затем откройте: ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "Логин: ${GREEN}${ADMIN_USERNAME}${NC}"
echo -e "Пароль: ${GREEN}${ADMIN_PASSWORD}${NC}"
echo ""
echo -e "${YELLOW}Caddy автоматически получит SSL сертификат. Это может занять минуту.${NC}"
