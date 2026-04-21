from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, abs as spark_abs, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, FloatType

schema = StructType([
    StructField("city", StringType(), True),
    StructField("temperature", FloatType(), True),
    StructField("humidity", FloatType(), True),
    StructField("timestamp", StringType(), True)
])

spark = SparkSession.builder \
    .appName("WeatherRealTimeProcessor") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.6.0"
    ) \
    .getOrCreate()

raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "weather_data") \
    .option("startingOffsets", "earliest") \
    .load()

weather_df = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))

def write_to_postgres(batch_df, epoch_id):
    if batch_df.rdd.isEmpty():
        return

    avg_df = batch_df.groupBy("city").agg(avg("temperature").alias("avg_temp"))

    result_df = batch_df.join(avg_df, "city") \
        .withColumn("is_anomaly", spark_abs(col("temperature") - col("avg_temp")) > 5) \
        .select("city", "timestamp", "avg_temp", "is_anomaly")

    db_url = "jdbc:postgresql://postgres:5432/weather"
    db_properties = {
        "user": "user",
        "password": "pass",
        "driver": "org.postgresql.Driver"
    }

    result_df.write.jdbc(
        url=db_url,
        table="weather_processed",
        mode="append",
        properties=db_properties
    )

query = weather_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_postgres) \
    .option("checkpointLocation", "/tmp/checkpoints_weather_v1") \
    .start()

query.awaitTermination()