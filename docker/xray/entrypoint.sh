#!/bin/sh
set -e

cfg=/etc/xray/config.json
echo "Waiting for $cfg..."

while true; do
  if [ -f "$cfg" ] && [ -s "$cfg" ]; then
    # есть непустой массив inbounds или явно tag "api"
    if grep -q '"inbounds"[[:space:]]*:[[:space:]]*\[' "$cfg" && \
       ! grep -q '"inbounds"[[:space:]]*:[[:space:]]*\[\s*\]' "$cfg"; then
      break
    fi
    if grep -q '"tag"[[:space:]]*:[[:space:]]*"api"' "$cfg"; then
      break
    fi
  fi
  sleep 1
done

exec xray run -c "$cfg"
