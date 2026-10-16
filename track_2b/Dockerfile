# Sigillum — Python standard library only: nothing is downloaded at runtime.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 10001 sigillum
WORKDIR /app
COPY pyproject.toml ./
COPY src/ src/
COPY data/ data/
RUN chown -R sigillum /app/data
USER sigillum
ENV PYTHONPATH=/app/src SIGILLUM_DATA=/app/data SIGILLUM_PORT=8080 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
CMD ["python", "-m", "sigillum", "serve"]
