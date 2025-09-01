# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlog_verilogica_orchestrator/Dockerfile

# ---------- Tools providers ----------
# BusyBox gives us a tiny wget (no shell required)
FROM busybox:1.36.1-uclibc AS bb

# curl + its deps (and certs)
FROM curlimages/curl:8.10.1 AS curlsrc


# ---------- FastAPI app image ----------

# Use a lean Python base image.
FROM python:3.13-slim AS fastapi

# Set the working directory inside the container.
WORKDIR /app

# Install system dependencies (curl + CA certificates)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the poetry configuration files into the container.
COPY ./pyproject.toml ./poetry.lock* ./

# Install the project's production dependencies.
RUN pip install poetry && poetry install --no-root --only main

# Copy the rest of the application code into the container.
COPY ./app ./app

# Expose the application's port.
EXPOSE 8000

# Command to run the application.
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



# ---------- eXist-DB image with wget + curl ----------
FROM existdb/existdb:latest AS existdb-with-tools
# Add wget as a BusyBox applet
COPY --from=bb /bin/busybox /bin/wget
# Add curl and runtime deps (certs + libs) so HTTPS works too
COPY --from=curlsrc /usr/bin/curl /usr/bin/curl
COPY --from=curlsrc /etc/ssl/certs/ /etc/ssl/certs/
COPY --from=curlsrc /usr/lib/ /usr/lib/
COPY --from=curlsrc /lib/ /lib/
