FROM jupyter/pyspark-notebook:spark-3.1.1

RUN pip3 install pyspark numpy 
RUN pip3 install elasticsearch==7.12.1
RUN pip3 install python-whois==0.8.0

WORKDIR /app

COPY ./code .

ENTRYPOINT ["spark-submit", "--packages", \
"org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.12.1", "--master", "local", "streaming.py"]