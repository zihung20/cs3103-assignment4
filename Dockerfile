FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Install iproute2 so we can run `tc` inside the container later
RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
