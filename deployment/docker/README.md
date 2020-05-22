# PySpark Plaso WebApp: Docker Image

## References

*	[SparkApp Docker Image](https://gitlab.com/rychly-edu/docker/docker-spark-app)

## Build

### The Latest Version by Docker

~~~sh
./fetch-app.sh
docker build --pull -t "registry.gitlab.com/rychly-edu/projects/pyspark-plaso:latest" .
~~~

### All Versions by the Build Script

~~~sh
./fetch-app.sh
./build.sh --build "registry.gitlab.com/rychly-edu/projects/pyspark-plaso" "latest"
~~~

For the list of versions to build see [docker-tags.txt file](docker-tags.txt).
