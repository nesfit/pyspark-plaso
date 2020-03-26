# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import sys
import zipfile
from functools import reduce
from io import BytesIO  # Python 3 way that should work also in Python 2
from os.path import basename, dirname
from tempfile import mkstemp

from flask import Response, Request, send_file
from pyarrow.lib import ArrowIOError

from controller import Controller
from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs


class FileManController(Controller):
    """
    Controller for HDFS-related management operations.
    """

    def __init__(self, hdfs_base_uri):
        # type: (str) -> None
        """
        Create a new controller that is able to store and utilize HDFS URI in HDFS queries and operations.
        :param hdfs_base_uri: the base HDFS URI to store
        """
        super(FileManController, self).__init__(hdfs_base_uri)
        self.hdfs = PyArrowHdfs()

    def ls(self, hdfs_path=""):
        # type: (str) -> Response
        """
        Get a Flask Response listing all files and directories (the dirs are suffixed by "/")
        that are in a given HDFS path.
        :param hdfs_path: the HDFS path to search for the files and directories
        :return: the Flask Response of the list of files and directories in the path
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        try:
            self.hdfs.open_filesystem(hdfs_uri)
            files_list = map(lambda path: self.strip_hdfs_uri(path), self.hdfs.list_files(hdfs_uri, sys.maxsize, True))
            result = Response(response=json.dumps(files_list),
                              status=200,
                              mimetype="application/json",
                              headers={"Content-Disposition": "inline;filename=dirs_and_files_list.json"})
            self.hdfs.close_filesystem()
        except ArrowIOError as e:
            result = Response(response="Error on the listing the directory/file: %s" % e,
                              status=400,
                              mimetype="text/plain")
        return result

    def rm(self, hdfs_path=""):
        # type: (str) -> Response
        """
        Get a Flask Response confirming a recursive removal of files and directories in a given HDFS path.
        :param hdfs_path: the HDFS path which should be removed including to remove its files and directories
        :return: the Flask Response of the confirmation of the remove
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        try:
            self.hdfs.open_filesystem(hdfs_uri)
            self.hdfs.remove(hdfs_uri, True)
            result = Response(
                response="OK, file/directory %s has been recursively removed!" % self.strip_hdfs_uri(hdfs_uri),
                status=200,
                mimetype="text/plain")
            self.hdfs.close_filesystem()
        except ArrowIOError as e:
            result = Response(response="Error on the removing the directory/file: %s" % e,
                              status=400,
                              mimetype="text/plain")
        return result

    def get(self, hdfs_path=""):
        # type: (str) -> Response
        """
        Get a Flask Response to download a file in a given HDFS path.
        :param hdfs_path: the HDFS path of the file to download
        :return: the Flask Response of the download
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        try:
            self.hdfs.open_filesystem(hdfs_uri)
            input_stream = self.hdfs.open_inputstream(hdfs_uri)
            result = Response(response=self.hdfs.read_inputstream(input_stream),
                              status=200,
                              mimetype="application/octet-stream",
                              headers={"Content-Disposition": "attachment;filename=%s" % basename(hdfs_uri)})
            self.hdfs.close_filesystem()
        except ArrowIOError as e:
            result = Response(response="Error on the getting file: %s" % e,
                              status=400,
                              mimetype="text/plain")
        return result

    def get_zip(self, hdfs_path=""):
        # type: (str) -> Response
        """
        Get a Flask Response to download a ZIP archive of files and directories in a given HDFS path.
        :param hdfs_path: the HDFS path which include into the ZIP archive
        :return: the Flask Response to download the ZIP file
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        try:
            self.hdfs.open_filesystem(hdfs_uri)
            # https://docs.python.org/2/library/tempfile.html#tempfile.mkstemp
            _, zip_file_name = mkstemp(suffix=".zip")
            # https://docs.python.org/2/library/zipfile.html#zipfile.ZipFile
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for hdfs_file in self.hdfs.list_files(hdfs_uri, sys.maxsize, False):
                    input_stream = self.hdfs.open_inputstream(hdfs_file)
                    file_name = self.strip_hdfs_uri(hdfs_file)
                    # https://docs.python.org/2/library/zipfile.html#zipfile.ZipFile.writestr
                    zip_file.writestr(file_name[1:], self.hdfs.read_inputstream(input_stream))
            # URIs ending with / have no basename so we need basename of their parent dirs
            download_name = basename(hdfs_uri) if hdfs_uri[-1] != '/' else basename(hdfs_uri[:-1])
            # https://flask.palletsprojects.com/en/master/api/#flask.send_file
            response = send_file(zip_file_name, "application/zip", True, "%s.zip" % download_name)
            self.hdfs.close_filesystem()
            return response
        except ArrowIOError as e:
            return Response(response="Error on the getting a ZIP archive for directory/file: %s" % e,
                            status=400,
                            mimetype="text/plain")

    def __upload_streamed_content(self, input_stream, hdfs_uri):
        # type: (BytesIO, str) -> Response
        """
        Upload a given stream into a HDFS file of a given HDFS URI.
        :param input_stream: the input stream to copy to the HDFS
        :param hdfs_uri: the HDFS URI where to upload the content from the stream
        :return: the Flask Response confirming the upload
        """
        try:
            self.hdfs.open_filesystem(hdfs_uri)
            self.hdfs.mkdir(dirname(hdfs_uri))
            # for a file, there must be a file name, not only its directory
            if hdfs_uri[-1] != '/':
                output_stream = self.hdfs.open_outputstream(hdfs_uri)
                self.hdfs.pass_to_outputstream(output_stream, input_stream)
            result = Response(response="OK, file/directory %s has been uploaded!" % self.strip_hdfs_uri(hdfs_uri),
                              status=200,
                              mimetype="text/plain")
            self.hdfs.close_filesystem()
        except ArrowIOError as e:
            result = Response(response="Error on the putting file: %s" % e,
                              status=400,
                              mimetype="text/plain")
        return result

    def put(self, request, hdfs_path):
        # type: (Request, str) -> Response
        """
        Copy the content uploaded by a PUT request in the REST API to a file in a given HDFS path.
        :param request: the REST API PUT request
        :param hdfs_path: the HDFS path where to upload
        :return: the Flask Response confirming the upload
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        # https://flask.palletsprojects.com/en/master/api/#flask.Request.stream
        input_stream = request.stream
        return self.__upload_streamed_content(input_stream, hdfs_uri)

    def put_form(self, request, hdfs_path):
        # type: (Request, str) -> Response
        """
        Copy the content uploaded by a HTML FORM to a file in a given HDFS path.
        :param request: the request which contains the FORM upload
        :param hdfs_path: the HDFS path where to upload
        :return: the Flask Response confirming the upload
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        # https://flask.palletsprojects.com/en/master/api/#flask.Request.files
        # https://werkzeug.palletsprojects.com/en/master/datastructures/#werkzeug.datastructures.FileStorage.stream
        input_stream = request.files['file'].stream
        return self.__upload_streamed_content(input_stream, hdfs_uri)

    @staticmethod
    def __reduce_responses(reduced, original):
        # type: (Response, Response) -> Response
        """
        Merge two Flask Responses into one. It can be utilized as a reduce function in reduce operation
        :param reduced: the first Response
        :param original: the second Response
        :return: the resulting merged Response
        """
        # https://flask.palletsprojects.com/en/master/api/#flask.Response
        return original if reduced is None else Response(
            response=reduced.data + "\n" + original.data,
            status=max(reduced.status_code, original.status_code),
            mimetype=reduced.mimetype
        )

    def __upload_streamed_zip_file(self, zip_data, hdfs_uri):
        # type: (str, str) -> Response
        """
        Extract the content of a ZIP archive in a given data buffer into a given HDFS URI.
        :param zip_data: the data buffer of the ZIP archive to extract into the HDFS
        :param hdfs_uri: the HDFS URI where to extract the ZIP content from the stream
        :return: the Flask Response confirming the upload
        """
        try:
            result = []
            with zipfile.ZipFile(BytesIO(zip_data)) as zip_file:
                for name in zip_file.namelist():
                    with zip_file.open(name, 'r') as input_stream:
                        file_name = hdfs_uri + "/" + name
                        result.append(self.__upload_streamed_content(input_stream, file_name))
            return reduce(self.__reduce_responses, result)
        except (zipfile.BadZipfile, zipfile.LargeZipFile) as e:
            return Response(response="Error on the extracting from a ZIP archive: %s" % e,
                            status=400,
                            mimetype="text/plain")

    def zip_put(self, request, hdfs_path=""):
        # type: (Request, str) -> Response
        """
        Extract the content of a ZIP archive uploaded by a PUT request in the REST API into a given HDFS path.
        :param request: the REST API PUT request
        :param hdfs_path: the HDFS path where to extract the ZIP archive
        :return: the Flask Response confirming the upload and extraction
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        # https://flask.palletsprojects.com/en/master/api/#flask.Request.stream
        input_stream = request.data
        # strip trailing *.zip filename from the hdfs_uri, because of putting should be in a directory only, see:
        # correct: curl "http://0.0.0.0:5432/zip/x/" --upload-file test.zip => http://0.0.0.0:5432/zip/x/test.zip
        # incorrect: curl "http://0.0.0.0:5432/zip/x" --upload-file test.zip => http://0.0.0.0:5432/zip/x
        return self.__upload_streamed_zip_file(input_stream, dirname(hdfs_uri))

    def zip_put_form(self, request, hdfs_path=""):
        # type: (Request, str) -> Response
        """
        Extract the content of a ZIP archive uploaded by a HTML FORM into a given HDFS path.
        :param request: the request which contains the FORM upload
        :param hdfs_path: the HDFS path where to extract the ZIP archive
        :return: the Flask Response confirming the upload and extraction
        """
        hdfs_uri = self.make_hdfs_uri(hdfs_path)
        # https://flask.palletsprojects.com/en/master/api/#flask.Request.files
        # https://werkzeug.palletsprojects.com/en/master/datastructures/#werkzeug.datastructures.FileStorage.stream
        input_stream = request.files['file'].stream
        return self.__upload_streamed_zip_file(input_stream, hdfs_uri)
