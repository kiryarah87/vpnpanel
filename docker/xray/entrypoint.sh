#!/bin/sh
# Ждём конфиг
while [ ! -f /etc/xray/config.json ]; do
  echo "Waiting for xray config..."
  sleep 2
done

exec xray run -c /etc/xray/config.json
