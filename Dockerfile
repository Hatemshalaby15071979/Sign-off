# Signoff Dockerfile — multi-stage, offline-capable, non-root.
# Build time (docker build) is the ONLY place network is used: wheels are
# downloaded once and vendor-baked into the final image. The final image has
# no network need and is tested with `docker run --network none` (see docs/).

# ---- Stage 1: builder — download pinned wheels ----------------------------
FROM python:3.11-slim AS builder

# Hashes are not verified manually here; exact pins reproduce the wheel set.
RUN mkdir -p /wheels
COPY pyproject.toml /tmp/pyproject.toml
RUN python -m pip download --only-binary=:all: --dest /wheels \
    "fpdf2==2.8.4" \
    "openpyxl==3.1.5" \
    && python -m pip download --only-binary=:all: --dest /wheels \
    "pytest==9.1.1" "pytest-cov==7.1.0" || true

# ---- Stage 2: runtime — install wheels offline, run as non-root -----------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY --from=builder /wheels /wheels

# Install the application dependency set WITHOUT network access.
RUN python -m pip install --no-index --find-links /wheels \
    "fpdf2==2.8.4" "openpyxl==3.1.5" \
    && rm -rf /wheels

WORKDIR /app
COPY src/ /app/src/
COPY scripts/ /app/scripts/

RUN python -m pip install --no-index --no-deps -e /app

# Non-root user; input is mounted read-only at /data, output writable at /out.
RUN useradd --create-home --shell /usr/sbin/nologin signoff \
    && mkdir -p /data /out \
    && chown -R signoff:signoff /app /out
USER signoff

# Entry point without shell so no accidental network or path tricks.
ENTRYPOINT ["python", "-m", "signoff"]
