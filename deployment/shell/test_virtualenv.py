# -*- coding: utf-8 -*-

if __name__ == "__main__":
    # Spark Session and Spark Context
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("PySpark VirtualEnv Test Application") \
        .getOrCreate()
    sc = spark.sparkContext

    # Python version
    import platform

    print("Spark with Python version %s" % platform.python_version())

    # Initialize Python environment
    # see https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.addPyFile
    sc.addPyFile("python/site-packages.zip")

    """test RDD"""
    print(sc.parallelize(range(1, 10)) \
          .collect())

    """get hostname and IP for 10 workers"""


    def test_nodeip(x):
        import socket
        s4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s4.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        return "%s[%s]" % (socket.gethostname(), s4.getsockname()[0])


    print(sc.parallelize(range(1, 10)) \
          .map(test_nodeip) \
          .collect())

    """test pyspark"""


    def test_pyspark(x):
        # see https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkFiles
        from pyspark import SparkFiles
        return SparkFiles.getRootDirectory()


    print(sc.parallelize(range(1, 10)) \
          .map(test_pyspark) \
          .collect())

    """test a custom Java class and PythonRDD-JavaRDD compatibility"""

    from pyspark.mllib.common import _py2java, _java2py

    debug_rdd_class = sc._gateway.jvm.tarzan.helpers.rdd.DebugRDD

    input_python_rdd = sc.parallelize(range(1, 10))
    input_java_rdd = _py2java(sc, input_python_rdd)
    print(debug_rdd_class.collectAndToString(input_java_rdd))
    output_java_rdd = debug_rdd_class.mapToString(input_java_rdd)
    output_python_rdd = _java2py(sc, output_java_rdd)
    print(output_python_rdd \
          .collect())

    # """test externally loaded Python package installer to install something on workers"""
    # def test_install(x):
    #  from custom_pip_package_dir import CustomPipPackageDir
    #  cppd = CustomPipPackageDir()
    #  return cppd.install("pefile")
    # print sc.parallelize(range(1,10)).map(test_install).collect()

    """test one of the externally loaded packages"""


    def test_pefile(x):
        import pefile
        return pefile.__version__


    print(sc.parallelize(range(1, 10)) \
          .map(test_pefile) \
          .collect())

    """test HDFS (pyarrow should be already in the Spark docker image)"""


    def test_hdfs(x):
        import pyarrow as pa
        # see https://arrow.apache.org/docs/python/filesystems.html#hadoop-file-system-hdfs
        fs = pa.hdfs.connect("namenode", 8020, user="hadoop")
        return "%d + %d = %d; /: %s" % (fs.get_space_used(), fs.df(), fs.get_capacity(), ' '.join(fs.ls('/')))


    print(sc.parallelize(range(1, 10)) \
          .map(test_hdfs) \
          .collect())

    """test HDFS custom module"""


    def test_hdfs_module(hdfs_uri):
        from plaso.tarzan.lib.pyarrow_hdfs import PyArrowHdfs
        py_arrow_hdfs = PyArrowHdfs()
        py_arrow_hdfs.open_filesystem(hdfs_uri)
        files = py_arrow_hdfs.list_files(hdfs_uri, 999)
        py_arrow_hdfs.close_filesystem()
        return files


    print(sc.parallelize(["hdfs://hadoop@namenode:8020/"]) \
          .flatMap(test_hdfs_module) \
          .collect())

    """test extractors"""

    list_files = test_hdfs_module
    test_data_files = sc.parallelize(["hdfs://hadoop@namenode:8020/test_data"]) \
        .flatMap(list_files) \
        .persist()

    """test PE extractor (FileObject-based)"""


    def test_pe_extractor(hdfs_uri):
        from plaso.tarzan.file.hdfs_file import HdfsFileObject
        file = HdfsFileObject()
        file.open(hdfs_uri)
        from plaso.parsers.pe import PEParser
        parser = PEParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        # parse and read results
        parser.Parse(mediator, file)
        return mediator.flush_buffer(exception_on_error=True)


    input_python_rdd = test_data_files \
        .filter(lambda x: x.endswith(".exe")) \
        .map(test_pe_extractor) \
        .persist()

    print("Number of events generated by the PE extractor: %d" % input_python_rdd.count())
    input_java_rdd = _py2java(sc, input_python_rdd)
    print(debug_rdd_class.collectAndToString(input_java_rdd))

    """test SQLite extractor (DFVFS-based)"""


    def test_sqlite_extractor(hdfs_uri):
        from dfvfs.path.factory import Factory as PathSpecFactory
        from dfvfs.resolver.resolver import Resolver as PathSpecResolver
        from plaso.tarzan.dfvfs2 import definitions
        pathSpec = PathSpecFactory.NewPathSpec(definitions.TYPE_INDICATOR_HDFS, location=hdfs_uri)
        file_entry = PathSpecResolver.OpenFileEntry(pathSpec)
        from plaso.parsers.sqlite import SQLiteParser
        parser = SQLiteParser()
        from plaso.tarzan.mediator.buffered_mediator import BufferedMediator
        mediator = BufferedMediator()
        mediator.SetFileEntry(file_entry)
        # parse and read results
        parser.Parse(mediator)
        return mediator.flush_buffer(exception_on_error=True)


    input_python_rdd = test_data_files \
        .filter(lambda x: x.endswith(".sqlite") or x.endswith("/History")) \
        .map(test_sqlite_extractor) \
        .persist()

    print("Number of events generated by the SQLite extractor: %d" % input_python_rdd.count())
    input_java_rdd = _py2java(sc, input_python_rdd)
    print(debug_rdd_class.collectAndToString(input_java_rdd))

    halyard_rdd_class = sc._gateway.jvm.tarzan.helpers.rdd.HalyardRDD
    input_python_rdd_flatten = input_python_rdd.flatMap(lambda x: x)
    input_java_rdd_flatten = _py2java(sc, input_python_rdd_flatten)
    halyard_rdd_class.saveToHalyard(input_java_rdd_flatten, "test", "zookeeper", 2181)