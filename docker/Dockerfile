FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock* .
COPY README.md .
RUN uv sync --no-dev

COPY . .

CMD uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000
