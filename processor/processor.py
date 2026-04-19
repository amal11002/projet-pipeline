from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, abs
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType

# Definition du schema des donnees entrantes
schema = StructType([
    StructField("city", StringType(), True),
    StructField("temperature", FloatType(), True),
    StructField("humidity", FloatType(), True),
    StructField("timestamp", TimestampType(), True)
])

# Initialisation de la Session Spark avec le connecteur Kafka 
spark = SparkSession.builder \
    .appName("WeatherRealTimeProcessor") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.6.0") \
    .getOrCreate()

# Lecture du flux en temps reel depuis le topic Kafka 'weather_data'
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "weather_data") \
    .load()

# Conversion du format binaire Kafka en colonnes exploitables
weather_df = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Calcul de la moyenne glissante sur 5 minutes 
# On utilise une fenetre de 5 minutes pour lisser les donnees
windowed_avg = weather_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "5 minutes"), col("city")) \
    .agg(avg("temperature").alias("avg_temp"))

# Detection d'anomalie 
# On compare la temperature actuelle à la moyenne de la fenetre.
# Une anomalie est detectee si : |temp_actuelle - avg_temp| > 5°C
final_df = weather_df.join(windowed_avg, "city") \
    .withColumn("is_anomaly", abs(col("temperature") - col("avg_temp")) > 5) \
    .select(
        col("city"), 
        col("timestamp"), 
        col("avg_temp"), 
        col("is_anomaly")
    )

# Fonction pour ecrire chaque micro-batch dans PostgreSQL 
def write_to_postgres(df, epoch_id):
    # Ces informations correspondent à ton docker-compose
    db_url = "jdbc:postgresql://postgres:5432/weather"
    db_properties = {
        "user": "user",
        "password": "pass",
        "driver": "org.postgresql.Driver"
    }
    # Ecriture dans la table creee precedemment 
    df.write.jdbc(url=db_url, table="weather_processed", mode="append", properties=db_properties)

# Lancement du streaming 
query = final_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()