# -*- coding: utf-8 -*-
"""PySpark Plaso processor"""

from __future__ import unicode_literals

import json
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
        # type: (SparkContext, RDD, str, str, int) -> int
        """
        Save the content of a given RDD with (HDFS URI, event) pairs into Halyard into a given table.
        :param sc: Spark Context of the RDD
        :param events_rdd: the RDD of (HDFS URI, event) paris to save
        :param table_name: Halyard repository HBase table name
        :param hbase_zk_quorum: HBase Zookeeper quorum of HBase config path
        :param hbase_zk_port: the Zookeeper client port
        :return: the processing time in nanoseconds
        """
        json_dumps_rdd = PySparkPlaso.transform_events_rdd_into_json_rdd(events_rdd)
        java_json_dumps_rdd = _py2java(sc, json_dumps_rdd)
        halyard_rdd_class = PySparkPlaso.get_java_rdd_helpers_package(sc).HalyardRDD
        return halyard_rdd_class.saveToHalyard(java_json_dumps_rdd, table_name, hbase_zk_quorum, hbase_zk_port)

    @staticmethod
    def json_dumper(obj):
        # type: (object) -> str
        """
        Dumps value of the object as a string which is useful as json.dumps default function to get a JSON serializable value.
        :param obj: the object to dump
        """
        import inspect
        # a variable without a dictionary is just converted to string
        if not hasattr(obj, '__dict__'):
            return str(obj)
        # otherwise, use the dictionary
        result = obj.__dict__
        # for a class instance, save its fully qualified class name
        if not inspect.isroutine(obj) and not inspect.isclass(obj):
            result["__class__"] = "{0}.{1}".format(obj.__class__.__module__, obj.__class__.__name__)
        return result

    @staticmethod
    def transform_events_rdd_into_json_rdd(events_rdd):
        # type: (RDD) -> RDD
        """
        Transform a given RDD with (HDFS URI, event) pairs into an RDD with JSON documents for each pair.
        :param events_rdd: the RDD of (HDFS URI, event) paris to transform
        :return the RDD of JSON documents
        """
        json_dumps_rdd = events_rdd.map(lambda event: json.dumps(event,
                                                                 default=PySparkPlaso.json_dumper,
                                                                 indent=2,
                                                                 separators=(',', ': '),
                                                                 sort_keys=True
                                                                 ))
        return json_dumps_rdd

    @staticmethod
    def action_events_rdd_by_collecting_into_json(events_rdd):
        # type: (RDD) -> str
        """
        Collects the content of a given RDD with (HDFS URI, event) pairs into a JSON documents collection.
        :param events_rdd: the RDD of (HDFS URI, event) paris to collect
        :return the JSON documents collection as a string
        """
        json_dumps_rdd = PySparkPlaso.transform_events_rdd_into_json_rdd(events_rdd)
        return "[\n" + ",\n".join(json_dumps_rdd.collect()) + "\n]"
