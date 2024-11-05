FROM python:3.9-slim

WORKDIR /app

COPY process_data.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "process_data.py"]
