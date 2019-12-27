# -*- coding: utf-8 -*-

from flask import Response
from pyspark import SparkContext

from controller import Controller
from plaso.tarzan.app.pyspark_plaso import PySparkPlaso


class PlasoController(Controller):
    """
    Controller for extraction of events by the Palso.
    """

    def __init__(self, hdfs_base_uri, spark_context):
        # type: (str, SparkContext) -> None
        """
        Create a new controller that will be utilizing HDFS URI and SparkContext.
        :param hdfs_base_uri: the base HDFS URI to store
        :param spark_context: the Spark context
        """
        super(PlasoController, self).__init__(hdfs_base_uri)
        self.spark_context = spark_context

    def extract(self, hdfs_path=""):
        # type: (str) -> Response
        """
        Run Plaso Extractors on a given HDFS path to generate events.
        :param hdfs_path: the path where to extract events from
        :return: the Flask Response with a JSON document of extracted events
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        files_rdd = PySparkPlaso.create_files_rdd(self.spark_context, hdfs_uri)
        events_rdd = PySparkPlaso.transform_files_rdd_to_extracted_events_rdd(self.spark_context, files_rdd)
        try:
            result = Response(
                response=PySparkPlaso.action_events_rdd_by_collecting_into_json(self.spark_context, events_rdd),
                status=200,
                mimetype="application/json",
                headers={"Content-Disposition": "inline;filename=extracted_events.json"})
        except Exception as e:
            result = Response(
                response="Error on the extraction: %s" % e,
                status=400,
                mimetype="text/plain")
        # TODO: remove when ready to save URIs
        # pure_events_rdd = events_rdd.map(lambda uri_event_pair: uri_event_pair[1])
        # PySparkPlaso.action_events_rdd_by_saving_into_halyard(pure_events_rdd, "plaso_sqlite_test", "zookeeper", 2181)
        return result
