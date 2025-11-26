FROM python:3.10-slim

WORKDIR /opt/application

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY model /opt/model

COPY --exclude=model . .

EXPOSE 5001

ENV PYTHONUNBUFFERED=1

RUN pytest --exitfirst --disable-warnings

CMD ["python", "-m", "app.app"]
