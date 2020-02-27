# -*- coding: utf-8 -*-
"""PySpark Plaso processor"""

from pyspark import SparkContext
from pyspark.mllib.common import _py2java
from pyspark.rdd import RDD

from extractors.manager import Manager


class PySparkPlaso(object):
    """
    Provides methods to create, modify, and evaluate RDD for the Plaso extraction.
    """

    @staticmethod
    def get_java_rdd_helpers_package(sc):
        # type: (SparkContext) -> object
        """
        Access a JVM gateway of the Spark Context and get Java package jvm.tarzan.helpers.rdd.
        :param sc: Spark Context
        :return: the Java package
        """
        return sc._gateway.jvm.tarzan.helpers.rdd

    @staticmethod
    def list_files(hdfs_uri):
        # type: (str) -> list
        """
        Get all files (recursively) from a given HDFS URI.
        :param hdfs_uri: the HDFS URI to get files from
        :return a list of HDFS URI in the given HDFS URI base-dir
        """
        from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs
        py_arrow_hdfs = PyArrowHdfs()
        py_arrow_hdfs.open_filesystem(hdfs_uri)
        files = py_arrow_hdfs.list_files(hdfs_uri, 999)
        py_arrow_hdfs.close_filesystem()
        return files

    @classmethod
    def create_files_rdd(cls, sc, hdfs_uri):
        # type: (SparkContext, str) -> RDD
        """
        Create a new RDD with HDFS URIs to all files (recursively) from the HDFS base URI.
        :param sc: Spark Context of the RDD
        :param hdfs_uri: the HDFS base URI
        :return the RDD of HDFS URIs
        """
        return sc.parallelize([hdfs_uri]).flatMap(
            lambda hdfs_sub_uri: cls.list_files(hdfs_sub_uri))

    @staticmethod
    def transform_files_rdd_to_extracted_events_rdd(sc, files_rdd):
        # type: (SparkContext, RDD) -> RDD
        """
        Transform RDD of HDFS URIs into a new RDDs of pairs produced by extractors where
        each pair consists of the HDFS URI of a file and one of event extracted from the file.
        :param sc: Spark Context of the RDD
        :param files_rdd: the RDD of HDFS URIs
        :return: the RDD of (HDFS URI, event) pairs
        """
        transformed_rdds = []
        for extractor in Manager.get_extractors():
            extracted_rdd = files_rdd \
                .filter(lambda hdfs_uri: extractor.filter(hdfs_uri)) \
                .flatMap(lambda hdfs_uri: map(lambda event: (hdfs_uri, event), extractor.extract(hdfs_uri)))
            # a magic! it is necessary to access the RDD before going to the next one in the further iterations
            # (e.g., by print or a method call); otherwise, the RDD wont be evaluated and will be overwritten
            # by the next one (so the list would contains several instances of the last RDD, nothing else)
            extracted_rdd.setName(extractor.__name__)
            transformed_rdds.append(extracted_rdd)
        return sc.union(transformed_rdds)

    @staticmethod
    def action_events_rdd_by_saving_into_halyard(sc, events_rdd, table_name, hbase_zk_quorum, hbase_zk_port):
        # type: (SparkContext, RDD, str, str, int) -> None
        """
        Save the content of a given RDD with (HDFS URI, event) pairs into Halyard into a given table.
        :param sc: Spark Context of the RDD
        :param events_rdd: the RDD of (HDFS URI, event) paris to save
        :param table_name: Halyard repository HBase table name
        :param hbase_zk_quorum: HBase Zookeeper quorum of HBase config path
        :param hbase_zk_port: the Zookeeper client port
        """
        java_events_rdd = _py2java(sc, events_rdd)
        halyard_rdd_class = PySparkPlaso.get_java_rdd_helpers_package(sc).HalyardRDD
        halyard_rdd_class.saveToHalyard(java_events_rdd, table_name, hbase_zk_quorum, hbase_zk_port)

    @staticmethod
    def action_events_rdd_by_collecting_into_json(sc, events_rdd):
        # type: (SparkContext, RDD) -> str
        """
        Collects the content of a given RDD with (HDFS URI, event) pairs into a JSON documents collection.
        :param sc: Spark Context of the RDD
        :param events_rdd: the RDD of (HDFS URI, event) paris to save
        :return the JSON documents collection as a string
        """
        java_events_rdd = _py2java(sc, events_rdd)
        json_rdd_class = PySparkPlaso.get_java_rdd_helpers_package(sc).JsonRDD
        return json_rdd_class.collectToJsonCollection(java_events_rdd)