# -*- coding: utf-8 -*-

import os
import sys

from pyspark import SparkContext

from plaso.tarzan.lib.hdfs import Hdfs


# BUG when using SparkContext for HDFS via Py4J on Spark workers:
# SPARK-5063, https://issues.apache.org/jira/browse/SPARK-5063
# It appears that you are attempting to reference SparkContext from a broadcast variable, action, or transformation.
# SparkContext can only be used on the driver, not in code that it run on workers.

class PySparkHdfs(Hdfs):
    """HDFS driver utilizing JVM gateway of the Spark Context."""

    # see also https://diogoalexandrefranco.github.io/interacting-with-hdfs-from-pyspark/

    def __init__(self, spark_context):
        # type: (SparkContext) -> None
        """
        Initialize the driver.
        :param spark_context: the Spark Context
        """
        self.spark_context = spark_context
        # ** load Java classes via PySpark Java Gateway
        # see https://cwiki.apache.org/confluence/display/SPARK/PySpark+Internals
        # see https://docs.oracle.com/javase/7/docs/api/java/net/URI.html
        self.uri_class = spark_context._gateway.jvm.java.net.URI
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/Path.html
        self.path_class = spark_context._gateway.jvm.org.apache.hadoop.fs.Path
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html
        self.fs_class = spark_context._gateway.jvm.org.apache.hadoop.fs.FileSystem
        # a helper Java class for an input stream reader to byte-array
        self.isr_class = spark_context._gateway.jvm.tarzan.helpers.py4j.InputStreamReader
        # ** other stateful properties
        self.fs = None

    def open_filesystem(self, hdfs_uri, user="hadoop"):
        # type: (str, str) -> object
        """
        Open HDFS filesystem of a given URI and as a given HDFS user.
        :param hdfs_uri: HDFS URI to open
        :param user: HDFS user to act as when opening
        :return: the opened filesystem as an object of org.apache.hadoop.fs.FileSystem class
        """
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#get(java.net.URI,%20org.apache.hadoop.conf.Configuration)
        self.fs = self.fs_class.get(self.uri_class(hdfs_uri), self.spark_context._jsc.hadoopConfiguration(), user)
        return self.fs

    def close_filesystem(self, filesystem=None):
        # type: (str) -> None
        """
        Close a given HDFS filesystem.
        :param filesystem: the filesystem
        """
        # by default, use the implicit filesystem
        if filesystem is None:
            filesystem = self.fs
            self.fs = None
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#close()
        filesystem.close()

    def make_path(self, path_string, qualified=True, filesystem=None):
        # type: (str, bool, object) -> str
        """
        Get a (qualified) HDFS URI from a given path and a given or a default filesystem.
        :param path_string: the path
        :param qualified: True to get the qualified path
        :param filesystem: the filesystem
        :return: the resulting path
        """
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/Path.html#Path(java.lang.String)
        path = self.path_class(path_string)
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#makeQualified(org.apache.hadoop.fs.Path)
        return filesystem.makeQualified(path) if (filesystem is not None) and qualified else path

    def append_to_path(self, original_path, new_child_string):
        # type: (str, str) -> str
        """
        Append a path/directory/file into another HDFS path.
        :param original_path: the another path
        :param new_child_string: the path to append
        :return: the resulting path
        """
        return self.path_class(original_path, new_child_string)

    def list_files(self, path_string, recursion_level=0, include_dir_names=False, filesystem=None):
        # type: (str, int, bool, object) -> list
        """
        Get a list of files (optionally recursively to the specified level) in a given HDFS path of a given filesystem.
        :param path_string: the path
        :param recursion_level: the level for the recursion (0 is just a current directory without any recursion)
        :param include_dir_names: True to include also names of directories (suffixed by /)
        :param filesystem: the filesystem
        :return: the list of files in the path
        """
        # exit on negative recursion level (cannot read the current level)
        if recursion_level < 0:
            return []
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # make path
        path = self.make_qualified_path(path_string, filesystem)
        # get items
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#listStatus(org.apache.hadoop.fs.Path)
        status_items = filesystem.listStatus(path)
        result = []
        for file_status in status_items:
            # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileStatus.html#getPath()
            status_path = file_status.getPath()
            if file_status.isFile():
                result.append(status_path)
            elif file_status.isDirectory():
                if include_dir_names:
                    result.append(status_path + "/")
                result.extend(self.list_files(status_path, recursion_level - 1, include_dir_names, filesystem))
        return result

    def open_inputstream(self, path, filesystem=None):
        # type: (str, object) -> object
        """
        Open and get an input-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened input-stream
        """
        # by default, use the implicit filesystem
        filesystem = self.get_filesystem(filesystem)
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#open(org.apache.hadoop.fs.Path)
        return filesystem.open(path)

    def close_stream(self, input_stream):
        # type: (object) -> None
        """
        Close a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        """
        # see https://docs.oracle.com/javase/7/docs/api/java/io/FilterInputStream.html#close()
        input_stream.close()

    def get_stream_offset(self, input_stream):
        # type: (object) -> int
        """
        Get the current position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param input_stream: the opened input-stream
        :return: the position/offset
        """
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FSDataInputStream.html#getPos()
        return input_stream.getPos()

    def get_path_size(self, path, filesystem=None):
        # type: (str, object) -> int
        """
        Get the size of a given HDFS path (a file) in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the size
        """
        # by default, use the implicit filesystem
        if filesystem is None:
            # see https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.getConf
            spark_conf = self.spark_context.getConf()
            # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/Path.html#getFileSystem(org.apache.hadoop.conf.Configuration)
            filesystem = self.fs if self.fs is not None else path.getFileSystem(spark_conf)
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/FileSystem.html#getUsed(org.apache.hadoop.fs.Path)
        return filesystem.getUsed(path)

    def read_inputstream(self, input_stream, size=sys.maxsize):
        # type: (object, int) -> bytes
        """
        Read data form a given opened input stream for a HDFS file.
        :param input_stream: the input-stream
        :param size: the size of data to read
        :return: the data
        """
        return self.read_inputstream_with_chunk(input_stream, size)

    def read_inputstream_with_chunk(self, input_stream, size=sys.maxsize, chunk_size=2048):
        # type: (object, int, int) -> bytes
        """
        Read data form a given opened input stream for a HDFS file.
        :param input_stream: the input-stream
        :param size: the size of data to read
        :param chunk_size: the size of a chunk
        :return: the data
        """
        result = ""
        # read the content into a buffer by chunks
        while True:
            # use InputStream read helper
            bac = self.isr_class.readInputStream(input_stream, min(size, chunk_size))
            # transfer the Java byte[] content into Python
            if bac.getSize() > 0:
                size = size - bac.getSize()
                result = result + bac.getBytes()
            else:
                size = -1
            # break when nothing to read or read the buffer of the given size
            if size <= 0:
                break
        return result

    def seek_stream(self, stream, offset, whence=os.SEEK_SET):
        # type: (object, int, int) -> None
        """
        Set a given position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param stream: the opened stream
        :param offset: the position/offset
        :param whence: the direction
        """
        return self.seek_stream_with_path(stream, offset, whence)

    def seek_stream_with_path(self, stream, offset, whence=os.SEEK_SET, path=None):
        # type: (object, int, int, str) -> None
        """
        Set a given position (an offset) in a given (previously opened) input-stream for a HDFS file.
        :param stream: the opened stream
        :param offset: the position/offset
        :param whence: the direction
        :param path: the path of the file required to be able to seek from the end of the file
        """
        # see https://hadoop.apache.org/docs/current/api/org/apache/hadoop/fs/Seekable.html#seek(long)
        if whence == os.SEEK_SET:
            stream.seek(offset)
        elif whence == os.SEEK_CUR:
            stream.seek(self.get_stream_offset(stream) + offset)
        elif whence == os.SEEK_END:
            stream.seek(self.get_path_size(path) + offset)

    def get_filesystem(self, force_filesystem):
        # type: (object) -> object
        """
        Get a given or a default HDFS filesystem.
        :param force_filesystem: the given filesystem
        :return: the filesystem
        """
        raise NotImplemented

    def exists(self, path_string, filesystem):
        # type: (str, object) -> bool
        """
        Check if a given HDFS path exists in the given HDFS filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: True if the path exists in the filesystem, False otherwise
        """
        raise NotImplemented

    def info(self, path_string, filesystem=None):
        # type: (str, object) -> dict
        """
        Get metadata of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        :return: the metadata dictionary
        """
        raise NotImplemented

    def remove(self, path_string, recursive=True, filesystem=None):
        # type: (str, bool, object) -> None
        """
        Remove (optionally recursively) a HDFS file/directory given by its path in a given or a default filesystem.
        :param path_string: the path
        :param recursive: True to remove recursively
        :param filesystem: the filesystem
        """
        raise NotImplemented

    def mkdir(self, path_string, filesystem=None):
        # type: (str, object) -> None
        """
        Make a new directory (if does not exist) of a given path in a given or a default filesystem.
        :param path_string: the path
        :param filesystem: the filesystem
        """
        raise NotImplemented

    def open_outputstream(self, path, filesystem=None):
        # type: (str, object) -> object
        """
        Open and get an output-stream for a HDFS file given by its path in a given filesystem.
        :param path: the path
        :param filesystem: the filesystem
        :return: the opened output-stream
        """
        raise NotImplemented

    def write_outputstream(self, output_stream, data):
        # type: (object, bytes) -> int
        """
        Write data buffer to a given opened output stream for a HDFS file.
        :param output_stream: the output-stream
        :param data: the data buffer to write
        :return: the number of bytes written
        """
        raise NotImplemented
