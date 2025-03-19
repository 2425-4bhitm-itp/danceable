FROM python:3.10-slim

WORKDIR /opt/application

COPY . /opt/application

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl
RUN apt-get install -y ffmpeg

EXPOSE 5001

ENV PYTHONUNBUFFERED=1

RUN pytest --exitfirst --disable-warnings

CMD ["python", "app.py"]
