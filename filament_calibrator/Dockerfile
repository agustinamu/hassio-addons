# Calibrador como addon de Home Assistant.
# Base Debian (glibc) para disponer de wheels de pydantic-core/uvloop sin compilar.
# uv gestiona el entorno reutilizando pyproject.toml / uv.lock (misma fuente que dev).
ARG BUILD_FROM=python:3.12-slim-bookworm
FROM ${BUILD_FROM}

# uv: binario estático desde la imagen oficial (sin pip).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    CALIBRATOR_DATA_DIR=/data

WORKDIR /app

# Capa de dependencias cacheable: solo los manifiestos antes que el código.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Código y contenido de calibración.
COPY app ./app
COPY content ./content

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
