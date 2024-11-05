FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the script and requirements
COPY download_data.py /app/
COPY requirements.txt /app/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "download_data.py"]
