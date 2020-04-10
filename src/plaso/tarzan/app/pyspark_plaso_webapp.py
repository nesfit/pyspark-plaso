# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import Flask, Response

from plaso.tarzan.app.views.extract2halyardview import ExtractToHalyardView
from plaso.tarzan.app.views.extractview import ExtractView
from plaso.tarzan.app.views.hdfsfileformview import HdfsFileFormView
from plaso.tarzan.app.views.hdfsfileview import HdfsFileView
from plaso.tarzan.app.views.hdfslsview import HdfsLsView
from plaso.tarzan.app.views.hdfsrmview import HdfsRmView
from plaso.tarzan.app.views.hdfszipformview import HdfsZipFormView
from plaso.tarzan.app.views.hdfszipview import HdfsZipView

app = Flask(__name__)


@app.route("/", methods=["GET"])
def app_list_routes():
    response = "<!DOCTYPE html>\n<html><title>%s</title><body><h1>%s</h1>\n" % (app.name, app.name)
    for rule in app.url_map.iter_rules():
        response += "<h2>%s</h2>\n" % rule.endpoint
        response += "<pre>[%s] %s</pre>\n" % (','.join(rule.methods), rule)
    response += "</body></html>"
    return Response(response=response,
                    status=200,
                    mimetype="text/html")


@app.after_request
def add_header(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Accept, Authorization, Cache-Control, Content-Type, Origin, X-Csrf-Token, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    return response


def configure_app(spark_context, hdfs_uri):
    # HDFS
    ls_view = HdfsLsView.as_view(str('hdfs_ls'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/ls/', defaults={'hdfs_path': ""}, view_func=ls_view, methods=['GET', ])
    app.add_url_rule('/ls/<path:hdfs_path>', view_func=ls_view, methods=['GET', ])
    rm_view = HdfsRmView.as_view(str('hdfs_rm'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/rm/<path:hdfs_path>', view_func=rm_view, methods=['GET', 'DELETE', ])
    file_view = HdfsFileView.as_view(str('hdfs_file'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/file/<path:hdfs_path>', view_func=file_view, methods=['GET', 'POST', 'DELETE', 'PUT', ])
    file_form_view = HdfsFileFormView.as_view(str('hdfs_file_form'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/file-form/<path:hdfs_path>', view_func=file_form_view,
                     methods=['GET', 'POST', 'DELETE', 'PUT', ])
    zip_view = HdfsZipView.as_view(str('hdfs_zip'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/zip/', defaults={'hdfs_path': ""}, view_func=zip_view, methods=['GET', 'POST', 'PUT', ])
    app.add_url_rule('/zip/<path:hdfs_path>', view_func=zip_view, methods=['GET', 'POST', 'DELETE', 'PUT', ])
    zip_form_view = HdfsZipFormView.as_view(str('hdfs_zip_form'), hdfs_base_uri=hdfs_uri)
    app.add_url_rule('/zip-form/', defaults={'hdfs_path': ""}, view_func=zip_form_view,
                     methods=['GET', 'POST', 'PUT', ])
    app.add_url_rule('/zip-form/<path:hdfs_path>', view_func=zip_form_view, methods=['GET', 'POST', 'DELETE', 'PUT', ])
    # Plaso extractor
    extract_view = ExtractView.as_view(str('plaso_extract'), hdfs_base_uri=hdfs_uri, spark_context=spark_context)
    app.add_url_rule('/extract/', defaults={'hdfs_path': ""}, view_func=extract_view, methods=['GET', ])
    app.add_url_rule('/extract/<path:hdfs_path>', view_func=extract_view, methods=['GET', ])
    extract2halyard_view = ExtractToHalyardView.as_view(str('plaso_extract_to_halyard'), hdfs_base_uri=hdfs_uri,
                                                        spark_context=spark_context)
    app.add_url_rule('/extract-to-halyard/', defaults={'hdfs_path': ""}, view_func=extract2halyard_view,
                     methods=['GET', ])
    app.add_url_rule('/extract-to-halyard/<path:hdfs_path>', view_func=extract2halyard_view, methods=['GET', ])
    return app
