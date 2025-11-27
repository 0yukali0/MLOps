FROM ubuntu
RUN apt-get update && apt-get install -y \
    nvidia-utils-535 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /root
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=ghcr.io/astral-sh/uv:0.9.13,source=/uv,target=/usr/bin/uv \
    --mount=type=bind,target=uv.lock,src=uv.lock \
    --mount=type=bind,target=pyproject.toml,src=pyproject.toml \
    uv sync -p 3.12 --no-dev --locked
WORKDIR /app
ENV PATH="/root/.venv/bin:$PATH" \
    UV_PYTHON=/root/.venv/bin/python
COPY main.py run.sh .
ENTRYPOINT ["nohup", "./run.sh"]