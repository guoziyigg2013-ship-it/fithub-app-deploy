FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV FITHUB_URL_PREFIX=/
ENV FITHUB_DATA_DIR=/data/fithub

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin fithub \
    && mkdir -p /data/fithub \
    && chown -R fithub:fithub /data /app

COPY --chown=fithub:fithub . /app

USER fithub

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/healthz' % os.getenv('PORT', '10000'), timeout=3).read()"

CMD ["python", "server.py"]
