# Signoff Dockerfile — multi-stage, offline-capable, non-root.
# Build time (docker build) is the ONLY place network is used: wheels are
# downloaded once and vendor-baked into the final image. The final image has
# no network need and is tested with `docker run --network none` (see docs/).

# ---- Stage 1: builder — download pinned, hash-verified wheels --------------
# Base image is digest-pinned so a tag move cannot change the build silently.
FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535 AS builder

COPY requirements.lock /tmp/requirements.lock
RUN mkdir -p /wheels
RUN python -m pip download --only-binary=:all: --dest /wheels \
    --require-hashes -r /tmp/requirements.lock

# ---- Stage 2: runtime — install wheels offline, run as non-root -----------
FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535 AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

COPY --from=builder /wheels /wheels

# Install the application dependency set WITHOUT network access, verifying
# every wheel against the SHA-256 hashes in requirements.lock.
COPY requirements.lock /app/requirements.lock
RUN python -m pip install --no-index --find-links /wheels \
    --require-hashes -r /app/requirements.lock \
    && rm -rf /wheels

WORKDIR /app
# pyproject.toml declares readme = "README.md" and license = { file = "LICENSE" },
# so both must be present for the editable install below to succeed.
COPY src/ /app/src/
COPY scripts/ /app/scripts/
# The `demo` command resolves fixtures via the /app fallback in cli.py.
COPY tests/fixtures/ /app/tests/fixtures/

# No pip install of the project itself: running from PYTHONPATH=/app/src avoids
# needing a build backend (setuptools) inside the offline runtime image.

# Non-root user; input is mounted read-only at /data, output writable at /out.
RUN useradd --create-home --shell /usr/sbin/nologin signoff \
    && mkdir -p /data /out \
    && chown -R signoff:signoff /app /out
USER signoff

# Entry point without shell so no accidental network or path tricks.
ENTRYPOINT ["python", "-m", "signoff"]
