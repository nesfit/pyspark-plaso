# TODO

## HDFS

	* use custome PySpark serializers for Event* objects, see https://chriscoughlin.com/2017/10/pyspark-serializers/

## Halyard

*	build/package of https://github.com/nesfit/timeline-analyzer/tree/master/timeline-spark
	*	exclude Hadoop deps in `pom.xml` (use external Haddop jars from Spark worker)
	*	requires another libs, see `../misc`
*	call the timeline-spark from PySpark work task
	* pass Event* object serialized by `pprint(vars(...))` as stdin
	* configure Zookeeper in args
	* usable for SQLite extractor only
