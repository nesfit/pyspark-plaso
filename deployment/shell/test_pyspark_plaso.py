# -*- coding: utf-8 -*-

if __name__ == "__main__":
    # Spark Session and Spark Context
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("PySpark Plaso Test Application") \
        .getOrCreate()
    sc = spark.sparkContext

    # Initialize Python environment
    # see https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.addPyFile
    sc.addPyFile("python/site-packages.zip")

    # Test PySpark Plaso
    from plaso.tarzan.app.pyspark_plaso import PySparkPlaso

    files_rdd = PySparkPlaso.create_files_rdd(sc, "hdfs://hadoop@namenode:8020/test_data")
    print("### Number of files to be analyzed by extractors: %d" % files_rdd.count())
    events_rdd = PySparkPlaso.transform_files_rdd_to_extracted_events_rdd(sc, files_rdd)
    print("### Number of events generated by extractors: %d" % events_rdd.count())
    print(PySparkPlaso.action_events_rdd_by_collecting_into_json(sc, events_rdd))
    print("### Saving the extracted events into Halyard ...")
    pure_events_rdd = events_rdd.map(lambda uri_event_pair: uri_event_pair[1])  # TODO: remove when ready to save URIs
    PySparkPlaso.action_events_rdd_by_saving_into_halyard(sc, pure_events_rdd, "test", "zookeeper", 2181)