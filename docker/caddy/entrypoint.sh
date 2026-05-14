#!/bin/sh
# Ждём конфиг
while [ ! -f /etc/caddy/Caddyfile ]; do
  echo "Waiting for Caddy config..."
  sleep 2
done

exec caddy run --config /etc/caddy/Caddyfile
