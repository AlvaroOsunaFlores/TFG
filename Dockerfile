FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends     gcc build-essential git     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel     && pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download es_core_news_sm  && python -m spacy download en_core_web_sm  && python -m spacy download fr_core_news_sm

COPY main.py .
COPY evaluate.py .
COPY model_loader.py .
COPY privacy_utils.py .
COPY reporting.py .
COPY api ./api
COPY scripts ./scripts
COPY docs ./docs

CMD ["python", "main.py"]
