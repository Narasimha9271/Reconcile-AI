FROM node:22-alpine AS dashboard
WORKDIR /web
COPY apps/web/package.json ./
RUN npm install
COPY apps/web/ ./
ENV STATIC_DASHBOARD=1 NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY services/api/pyproject.toml ./
RUN pip install --no-cache-dir .
COPY services/api/src ./src
COPY services/api/migrations ./migrations
COPY --from=dashboard /web/out ./dashboard
ENV PYTHONPATH=/app/src
CMD ["sh", "-c", "exec uvicorn reconcileai.main:app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]
