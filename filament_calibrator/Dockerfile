# Calibrador como addon de Home Assistant.
# Base Debian (glibc) para disponer de wheels de pydantic-core/uvloop sin compilar.
# uv gestiona el entorno reutilizando pyproject.toml / uv.lock (misma fuente que dev).
# FROM literales (etiqueta + digest) para que Dependabot los actualice.
FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv
FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

# uv: binario estático desde la imagen oficial (sin pip).
COPY --from=uv /uv /uvx /usr/local/bin/

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
