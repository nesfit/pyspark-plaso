# Running Plaso Extractors in PySpark

## Python Virtual Environment

### PyCharm

*	be ready to use PySpark (e.g., go to `nix-shell`)
*	make a Python symlink by `./python/make-python-symlink.sh`
*	open PyCharm and "Add Python Interpreter" as "Virtualenv Environment" / "New environment" with "Base interpreter" set to the Python symlink above
*	close the PyCharm and remove the `../venv` directory with the just-created Virtualenv environment

### Virtualenv

*	be ready to use PySpark (e.g., go to `nix-shell`)
*	run `./python/make-virtual-env.sh`

## Requirements

### Use Java Helpers and Another Java Libraries

The Spark/HDFS tasks below require Java helpers and another Java libraries. It is necessary to build them before running the tasks.

~~~sh
./java/make-timeline-analyzer-spark.sh
./java/make-pyspark-java-helpers.sh
ls -l ./java/*.jar
~~~

Note that the following methods do not seem to work to import JAR files:

*	`spark = SparkSession.builder.*.config('spark.jars', "full-path-to-library.jar").*`
*	`spark_context._jsc.addJar("full-path-to-library.jar")`
*	`spark_context.addPyFile("full-path-to-library.jar")`

### Use Ptyhon Packages by PySpark with `SparkContext.addPyFile`

~~~sh
./python/make-virtual-env.sh
./python/make-site-packages-zip.sh
grep -F 'site-packages.zip' *.py # result: sc.addPyFile("site-packages.zip")
~~~

### Start Docker Containers for a Spark/HDFS/HBase Cluster

The docker containers can be started by `cd docker && docker-compose up`.

*	`docker-compose-standalone.yml` -- Spark Standalone cluster (stable)
*	`docker-compose-yarn.yml` -- YARN cluster (still work-in-progress)

### HBase Table and Halyard Repository

Run Halyard SDK in a new Docker container and open its interactive login shell:

~~~sh
./docker/run-docker-halyard-sdk.sh
~~~

In the container, open Halyard's RDF4J Console:

~~~sh
console
~~~

In the console, create a new HBase-based repository of ID 'plaso_sqlite_test':

~~~
create hbase
# Repository ID: plaso_sqlite_test
open plaso_sqlite_test
quit
~~~

#### Checking HBase Table/Halyard Repository

In the container, open Halyard's RDF4J Console:

~~~sh
console
~~~

In the console, open the HBase-based repository of ID 'plaso_sqlite_test':

~~~
open plaso_sqlite_test
quit
~~~

The content of the created HBased table can be listed by:

~~~sh
hbase shell
~~~

and in the shell:

~~~
scan 'plaso_sqlite_test'
count 'plaso_sqlite_test', { INTERVAL => 1 }
~~~

### Client for Spark and Hadoop

#### In NixOS

Run the provided nix-shell with the correct versions of Spark, Hadoop, and Python:

*	`nix-shell shell.nix`

### Upload HDFS Files

*	Use one of `hadoop fs` (for mixed filesystems) or `hdfs dfs` for HDFS filesystems (not `hdfs fs`).

Upload a test data into HDFS by:

~~~sh
./hdfs-upload-test-data.sh
~~~

## Run the Task on the Spark/HDFS/HBase Cluster

*	In the case of a client behind a firewall, it is necesasry to set and to enable a Spark driver/client ports.
	See `spark-submit-py-to-docker-standalone.sh` for details.

~~~sh
./test_virtualenv.sh # see spark-submit-py-to-docker-standalone.sh
~~~

## Useful References

### Plaso

*	[Digital Forensics SIFT'ing: Cheating Timelines with log2timeline](https://digital-forensics.sans.org/blog/2011/12/16/digital-forensics-sifting-cheating-timelines-with-log2timeline)

### REST API

*	Building a Movie Recommendation Service with Apache Spark & Flask:
	[part 1](https://www.codementor.io/jadianes/building-a-recommender-with-apache-spark-python-example-app-part1-du1083qbw),
	[part 2](https://www.codementor.io/jadianes/building-a-web-service-with-apache-spark-flask-example-app-part2-du1083854)
*	[Uploading and Downloading Files with Flask](https://stackoverflow.com/a/27638470/5265908)
*	[Flask WebHDFS](https://github.com/thanhson1085/flask-webhdfs/blob/master/app/example/controllers.py)

### PySpark

#### Custom Packages

*	https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.addPyFile
*	https://docs.python.org/2.7/library/zipfile.html#zipfile.PyZipFile.writepy

#### VirtualEnv

*	https://community.hortonworks.com/articles/104947/using-virtualenv-with-pyspark.html
*	https://issues.apache.org/jira/browse/SPARK-13587
*	https://docs.anaconda.com/anaconda-scale/howto/spark-configuration/
*	https://www.questarter.com/q/running-python-in-yarn-spark-cluster-mode-using-virtualenv-27_45202045.html

#### Anaconda Environment

*	set-up virtualenvironment/conda
*	run pyspark with the environment and a sample task
*	use an plaso extractor in RDD/SQL in pyspark

### NixOS

*	https://nixos.wiki/wiki/Python
*	https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
*	https://github.com/NixOS/nixpkgs/blob/master/pkgs/applications/networking/cluster/spark/default.nix
