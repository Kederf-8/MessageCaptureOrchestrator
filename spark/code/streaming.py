from elasticsearch import Elasticsearch

# our modules
from geocoding import find_cities_in_text, get_location_as_string
from sentimentAnalysis import cleanText, getModel, saveModel
from urlScraper import ensure_protocol, find_all_urls, load_and_parse
from whoIsManager import WhoIsManager

from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import types as st
from pyspark.sql.functions import col, explode, from_json, udf

TOPIC = "telegram-messages"
KAFKASERVER = "kafkaserver:29092"
# KAFKASERVER = "localhost:9092"

es_first_index = "webpages_content"
es_second_index = "ukraine_cities"

whoIs = WhoIsManager()
extractUrls = udf(
    lambda x: ensure_protocol(find_all_urls(x)), st.ArrayType(elementType=st.StringType())
)
getTextFromHtml = udf(load_and_parse)
udf_cleanText = udf(cleanText)
udf_whois = udf(whoIs.get_relevant_fields)
equivalent_emotion = udf(lambda x: "positive" if x == 1.0 else "negative")
ukrainian_cities = udf(find_cities_in_text, st.ArrayType(st.StringType()))
city_location = udf(get_location_as_string)


def get_spark_session():
    spark_conf = SparkConf().set("es.nodes", "elasticsearch").set("es.port", "9200")
    sc = SparkContext(appName="spark-to-es", conf=spark_conf)
    return SparkSession(sc)


def get_record_schema():
    return st.StructType(
        [
            st.StructField("id", st.StringType(), nullable=True),
            st.StructField("data", st.StringType(), nullable=True),
            st.StructField("channel", st.StringType(), nullable=True),
            st.StructField("authorName", st.StringType(), nullable=True),
            st.StructField("authorLink", st.StringType(), nullable=True),
            st.StructField(
                "images", st.ArrayType(elementType=st.StringType()), nullable=True
            ),
            st.StructField(
                "text", st.ArrayType(elementType=st.StringType()), nullable=True
            ),
            st.StructField(
                "videos", st.ArrayType(elementType=st.StringType()), nullable=True
            ),
            st.StructField("views", st.StringType(), nullable=True),
            st.StructField("translation", st.StringType(), nullable=True),
            st.StructField("@timestamp", st.StringType(), nullable=True),
        ]
    )


def get_tr_schema():
    return st.StructType(
        [
            st.StructField("service", st.StringType(), nullable=True),
            st.StructField("text", st.StringType(), nullable=True),
        ]
    )


def get_elastic_schema():
    return {
        "mappings": {
            "properties": {
                "id": {"type": "text"},
                "channel": {"type": "text"},
                "url": {"type": "text"},
                "@timestamp": {"type": "date", "format": "epoch_second"},
                "content": {"type": "text"},
            }
        }
    }


# Create a Spark Session
spark = get_spark_session()

spark.sparkContext.setLogLevel("ERROR")

schema = get_record_schema()

tr_schema = get_tr_schema()

es_mapping = get_elastic_schema()


def getReader(mode=""):
    if mode == "test":
        return (
            spark.readStream.format("socket")
            .option("host", "localhost")
            .option("port", 9997)
            .option("startingOffsets", "latest")
            .load()
        )

    # Read data from Kafka
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKASERVER)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )


def outputStream(stream, mode="", index=""):
    if mode == "test":
        return stream.writeStream.outputMode("append").format("console").start()
    else:
        es = Elasticsearch("http://elasticsearch:9200")

        response = es.indices.create(index=index, ignore=400)

        if "acknowledged" in response:
            if response["acknowledged"] is True:
                print("Successfully created index:", response["index"])

        write = (
            stream.writeStream.option("checkpointLocation", "/tmp/")
            .format("es")
            .start(index)
        )

        return write


# Pipeline emotion_detection
pipelineFit = getModel(task="emotion_detection", inputCol="content", labelCol="label")
saveModel(pipelineFit, task="emotion_detection")


df = (
    getReader()
    .select(from_json(col("value").cast("string"), schema).alias("data"))
    .selectExpr("data.*")
)

# df.printSchema()

# Split the list into sentences
sentences = df.select(
    col("id"),
    col("channel"),
    col("@timestamp"),
    col("data"),
    explode(df.text).alias("sentence"),
)
# sentences.printSchema()

message_analysis = (
    df.select(
        col("id"),
        col("channel"),
        col("@timestamp").alias("timestamp"),
        from_json(col("translation").cast("string"), tr_schema).alias("tr"),
    )
    .selectExpr("id", "channel", "timestamp", "tr.*")
    .select("id", "channel", "timestamp", udf_cleanText("text").alias("content"))
)

# Extract Urls from sentences
urls = sentences.select(
    col("id"),
    col("channel"),
    col("@timestamp"),
    col("data"),
    explode(extractUrls(col("sentence"))).alias("url"),
)

# urls.printSchema()

# add text from html webpage and whois info
df = urls.withColumn("content", udf_cleanText(getTextFromHtml(urls.url))).withColumn(
    "whois", udf_whois(urls.url)
)

# df.printSchema()

# Sentiment Analysis: emotion_detection
out_df = (
    pipelineFit.transform(df)
    .withColumn("emotion_detection", equivalent_emotion(col("prediction")))
    .select(
        "id", "channel", "@timestamp", "content", "url", "whois", "emotion_detection"
    )
)

message_analysis = (
    pipelineFit.transform(message_analysis)
    .withColumn("emotion_detection", equivalent_emotion(col("prediction")))
    .select(
        "id",
        "channel",
        "timestamp",
        col("content").alias("traduction"),
        "emotion_detection",
    )
    .withColumn("city", explode(ukrainian_cities(col("traduction"))))
    .withColumn("location", city_location(col("city")))
)  # esclusivamente città ucraine

# col('prediction')
# out_df.printSchema()
# out_df.explain()

# message_analysis.printSchema()
# message_analysis.explain()

out_stream = outputStream(out_df, index=es_first_index)
out_stream2 = outputStream(message_analysis, index=es_second_index)

out_stream.awaitTermination()
out_stream2.awaitTermination()

spark.stop()
