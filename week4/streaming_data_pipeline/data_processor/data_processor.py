import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg
from pyspark.sql.types import StructType, StructField, IntegerType, LongType

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_stream():
    kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'test_topic')
    postgres_url = os.getenv('POSTGRES_URL', 'jdbc:postgresql://postgres:5432/streaming_db')
    postgres_properties = {
        'user': os.getenv('POSTGRES_USER', 'airflow'),
        'password': os.getenv('POSTGRES_PASSWORD', 'airflow'),
        'driver': 'org.postgresql.Driver'
    }

    logger.info(f"Starting Spark Session to consume from Kafka topic '{kafka_topic}'")

    spark = SparkSession.builder \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    schema = StructType([
        StructField("timestamp", LongType(), True),
        StructField("value", IntegerType(), True)
    ])

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .load()

    json_df = df.selectExpr("CAST(value AS STRING)") \
                .select(from_json(col("value"), schema).alias("data")) \
                .select("data.*")

    # Perform transformations
    transformed_df = json_df.groupBy().agg(avg("value").alias("average_value"))

    # Write the transformed data to PostgreSQL
    query = transformed_df \
        .writeStream \
        .outputMode("complete") \
        .foreachBatch(lambda batch_df, batch_id: batch_df.write \
            .jdbc(url=postgres_url, table='aggregated_data', mode='append', properties=postgres_properties)) \
        .start()

    logger.info("Started streaming query to process data")

    query.awaitTermination()


if __name__ == "__main__":
    process_stream()
