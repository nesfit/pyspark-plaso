# -*- coding: utf-8 -*-

if __name__ == "__main__":
    # Spark Session and Spark Context
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("PySpark VirtualEnv Test Application") \
        .getOrCreate()
    sc = spark.sparkContext

    # Initialize Python environment
    # see https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.addPyFile
    sc.addPyFile("python/site-packages.zip")

    def list_files(hdfs_uri):
        from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs
        py_arrow_hdfs = PyArrowHdfs()
        py_arrow_hdfs.open_filesystem(hdfs_uri)
        files = py_arrow_hdfs.list_files(hdfs_uri, 999)
        py_arrow_hdfs.close_filesystem()
        return files

    def test_sqlite_extractor(hdfs_uri):
        from dfvfs.path.factory import Factory as PathSpecFactory
        from dfvfs.resolver.resolver import Resolver as PathSpecResolver
        from plaso.tarzan.dfvfs2 import definitions
        pathSpec = PathSpecFactory.NewPathSpec(definitions.TYPE_INDICATOR_HDFS, location=hdfs_uri)
        file_entry = PathSpecResolver.OpenFileEntry(pathSpec)
        from plaso.parsers.sqlite import SQLiteParser
        parser = SQLiteParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        mediator.SetFileEntry(file_entry)
        # parse and read results
        parser.Parse(mediator)
        return mediator.flush_buffer(exception_on_error=True)

    test_data_files = sc.parallelize(["hdfs://hadoop@namenode:8020/test_data/demo-2019-09"]) \
        .flatMap(list_files) \
        .persist()

    print(test_data_files \
          .collect())

    input_python_rdd = test_data_files \
        .filter(lambda x: x.endswith(".sqlite") or x.endswith("/History")) \
        .map(test_sqlite_extractor) \
        .persist()

    from pyspark.mllib.common import _py2java, _java2py
    debug_rdd_class = sc._gateway.jvm.tarzan.helpers.rdd.DebugRDD
    halyard_rdd_class = sc._gateway.jvm.tarzan.helpers.rdd.HalyardRDD

    input_python_rdd_flatten = input_python_rdd.flatMap(lambda x: x)
    input_java_rdd_flatten = _py2java(sc, input_python_rdd_flatten)

    print(input_python_rdd_flatten \
          .collect())

    print(debug_rdd_class.collectAndToString(input_java_rdd_flatten))

    halyard_rdd_class.saveToHalyard(input_java_rdd_flatten, "test", "zookeeper", 2181)
