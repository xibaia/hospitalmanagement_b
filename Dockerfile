FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpangocairo-1.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt /app/
RUN pip install --no-cache-dir -r requirement.txt

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "hospitalmanagement.wsgi:application", "--bind", "0.0.0.0:8000"]
