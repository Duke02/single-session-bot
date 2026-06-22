FROM python:3.12-slim-trixie

RUN apt update && \
    apt install -y python3-dev python-is-python3 

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /bot

COPY single-session .
