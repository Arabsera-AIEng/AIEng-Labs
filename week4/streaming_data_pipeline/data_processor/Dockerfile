# Dockerfile for Data Processor
FROM openjdk:17-jdk-slim

# Install Python, pip, and necessary utilities
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget curl procps && \
    rm -rf /var/lib/apt/lists/*

# Install Spark
RUN wget https://archive.apache.org/dist/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz && \
    tar xzf spark-3.4.4-bin-hadoop3.tgz -C /opt && \
    rm spark-3.4.4-bin-hadoop3.tgz

# Set environment variables
ENV SPARK_HOME=/opt/spark-3.4.4-bin-hadoop3
ENV PATH=$PATH:$SPARK_HOME/bin

# Install pyspark and kafka-python
RUN pip3 install pyspark==3.4.4 kafka-python

# Copy the data_processor.py script
COPY data_processor.py /app/data_processor.py

WORKDIR /app

# Set the entrypoint to spark-submit
ENTRYPOINT ["spark-submit"]
