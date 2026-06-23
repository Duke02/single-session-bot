FROM python:3.14-slim-trixie

RUN apt update && \
    apt install -y python3-dev python-is-python3 

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /bot

COPY .env .

COPY pyproject.toml .
COPY uv.lock . 
COPY .python-version .

RUN uv sync 

COPY ./single_session/ ./single_session


CMD ["uv", "run", "python", "-m", "single_session.bot"]