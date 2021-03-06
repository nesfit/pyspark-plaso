# -*- coding: utf-8 -*-

if __name__ == "__main__":
    # Spark Session and Spark Context
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("PySpark Plaso WebAPI Application") \
        .getOrCreate()
    sc = spark.sparkContext

    from os import getenv

    from plaso.tarzan.app.pyspark_plaso_webapp import configure_app
    app = configure_app(sc, getenv("PP_HDFS_URI", "hdfs://hadoop@namenode:8020/test_data"))

    # Enable WSGI access logging via Paste
    from paste.translogger import TransLogger
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    import cherrypy
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload.on': True,
        'log.screen': True,
        'server.socket_port': int(getenv("PP_PORT", 54380)),
        'server.socket_host': getenv("PP_HOST", '0.0.0.0'),
        # remove size-limit for file uploads
        'server.max_request_body_size': 0,
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()
