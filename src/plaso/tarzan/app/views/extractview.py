# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask.views import MethodView

from plaso.tarzan.app.controllers.plasocontroller import PlasoController


class ExtractView(MethodView):
    def __init__(self, hdfs_base_uri, spark_context):
        self.controller = PlasoController(hdfs_base_uri, spark_context)

    def get(self, hdfs_path=""):
        return self.controller.extract(hdfs_path)
