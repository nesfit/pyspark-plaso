# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import request
from flask.views import MethodView

from plaso.tarzan.app.controllers.filemancontroller import FileManController


class HdfsFileFormView(MethodView):
    def __init__(self, hdfs_base_uri):
        self.controller = FileManController(hdfs_base_uri)

    def get(self, hdfs_path=""):
        return self.controller.get(hdfs_path)

    def post(self, hdfs_path=""):
        return self.controller.put_form(request, hdfs_path)

    def delete(self, hdfs_path=""):
        return self.controller.rm(hdfs_path)

    def put(self, hdfs_path=""):
        return self.controller.put_form(request, hdfs_path)
