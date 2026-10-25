# Calibrador como addon de Home Assistant.
# Base Debian (glibc) para disponer de wheels de pydantic-core/uvloop sin compilar.
# uv gestiona el entorno reutilizando pyproject.toml / uv.lock (misma fuente que dev).
# FROM literales (etiqueta + digest) para que Dependabot los actualice.
FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv
FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70

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
