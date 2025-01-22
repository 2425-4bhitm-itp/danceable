FROM python:3.10-slim

WORKDIR /opt/application

COPY . /opt/application

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "ml_service.py"]
