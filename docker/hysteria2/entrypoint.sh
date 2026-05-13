#!/bin/sh

echo "Waiting for valid Hysteria2 config..."

while true; do
  if [ -f /etc/hysteria2/config.yaml ]; then
    # Проверяем что конфиг содержит tls секцию
    if grep -q "^tls:" /etc/hysteria2/config.yaml; then
      echo "Valid config found, starting Hysteria2..."
      exec hysteria server -c /etc/hysteria2/config.yaml
    fi
  fi
  echo "Config not ready yet, waiting..."
  sleep 5
done
