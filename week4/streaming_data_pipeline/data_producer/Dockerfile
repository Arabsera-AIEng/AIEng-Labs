# Dockerfile for Data Producer
FROM python:3.9-slim

RUN pip install kafka-python

COPY data_producer.py /app/data_producer.py

WORKDIR /app

CMD ["python", "data_producer.py"]