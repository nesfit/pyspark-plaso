# -*- coding: utf-8 -*-
from flask import request
from flask.views import MethodView

from plaso.tarzan.app.controllers.filemancontroller import FileManController


class HdfsZipView(MethodView):
    def __init__(self, hdfs_base_uri):
        self.controller = FileManController(hdfs_base_uri)

    def get(self, hdfs_path=""):
        return self.controller.get_zip(hdfs_path)

    def post(self, hdfs_path=""):
        return self.controller.zip_put(request, hdfs_path)

    def delete(self, hdfs_path=""):
        return self.controller.rm(hdfs_path)

    def put(self, hdfs_path=""):
        return self.controller.zip_put(request, hdfs_path)
