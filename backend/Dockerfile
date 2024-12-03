FROM python:3.13.0-slim

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     gcc \
     libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY ./backend/requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
