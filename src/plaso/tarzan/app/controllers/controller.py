# -*- coding: utf-8 -*-


class Controller(object):
    """
    Base-class for controllers.
    """

    def __init__(self, hdfs_base_uri):
        # type: (str) -> None
        """
        Create a new controller that is able to store and utilize HDFS URI.
        :param hdfs_base_uri: the base HDFS URI to store
        """
        self.hdfs_base_uri = hdfs_base_uri

    def make_hdfs_uri(self, hdfs_path):
        # type: (str) -> str
        """
        Get a full HDFS URI by adding a given path to the base HDFS URI.
        :param hdfs_path: HDFS path
        :return: HDFS URI
        """
        return self.hdfs_base_uri + "/" + hdfs_path

    def strip_hdfs_uri(self, hdfs_path):
        # type: (str) -> str
        """
        Get a given HDFS path without its HDFS URI prefix.
        :param hdfs_path: the HDFS path
        :return: the HDFS path without the HDFS URI prefix
        """
        return hdfs_path[len(self.hdfs_base_uri):] if hdfs_path.startswith(self.hdfs_base_uri) else hdfs_path
