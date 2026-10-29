# Calibrador como addon de Home Assistant.
# Base Debian (glibc) para disponer de wheels de pydantic-core/uvloop sin compilar.
# uv gestiona el entorno reutilizando pyproject.toml / uv.lock (misma fuente que dev).
# FROM literales (etiqueta + digest) para que Dependabot los actualice.
FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv
FROM python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337

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
