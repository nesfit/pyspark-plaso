# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask.views import MethodView

from plaso.tarzan.app.controllers.filemancontroller import FileManController


class HdfsRmView(MethodView):
    def __init__(self, hdfs_base_uri):
        self.controller = FileManController(hdfs_base_uri)

    def get(self, hdfs_path=""):
        return self.controller.rm(hdfs_path)

    def delete(self, hdfs_path=""):
        return self.controller.rm(hdfs_path)
