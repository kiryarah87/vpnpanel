FROM node:20-alpine AS frontend_builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM caddy:latest
COPY --from=frontend_builder /app/dist /srv/frontend
COPY app/config_gen/configs/caddy/decoy /srv/decoy
COPY docker/caddy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
