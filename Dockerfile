FROM python:3.10-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app /usr/src/app

ENV PYTHONPATH=${PYTHONPATH}:/usr/src/app
EXPOSE 8000

CMD ["/bin/sh", "./start.sh"]
