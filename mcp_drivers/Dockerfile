FROM alpine:3.21
WORKDIR /root
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=ghcr.io/astral-sh/uv:0.9.8,source=/uv,target=/usr/bin/uv \
    --mount=type=bind,target=uv.lock,src=uv.lock \
    --mount=type=bind,target=pyproject.toml,src=pyproject.toml \
    uv sync --locked --no-dev
ENV PATH="/root/.venv/bin:$PATH" \
    UV_PYTHON=/root/.venv/bin/python
COPY weather_server.py main.py