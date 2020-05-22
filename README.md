# pyspark-plaso

(c) 2018-2020 Marek Rychly (rychly@fit.vutbr.cz) and Radek Burget (burgetr@fit.vutbr.cz)

A tool for distributed extraction of timestamps from various files using extractors adapted from the Plaso engine to Apache Spark.

## Usage

The PySpark Plaso is running in a Docker container and it is accessible as a Web service via a REST API.

See the project Wiki Pages for details.

## Use a Prebuilt Docker Image

There is [a prebuilt Docker image](https://gitlab.com/rychly-edu/projects/pyspark-plaso/container_registry).

See the [webapp-prebuilt.yml](deployment/docker-compose/webapp-prebuilt.yml) docker-compose file.

## Build and Deploy

~~~
cd ./deployment
# create a Python virtual environment including a required Python packages
./010-make-python-virtualenv.sh
# pack the Python packages into a ZIP file ready to use in PySpark
./020-make-site-packages-zip.sh
# create JAR packages for Java dependencies
./030-make-java-helpers.sh
# run the PySpark Plaso infrastructure as Docker containers by docker-compose
./040-run-docker-webapp.sh
~~~

See the project Wiki Pages for details and also the [webapp.yml](deployment/docker-compose/webapp.yml) docker-compose file.

## Dependencies

The PySpark Plaso is

*	utilizing extractors adapted from the [Plaso Project](https://github.com/log2timeline/plaso)
*	running at Docker containers from the [TARZAN Docker Infrastructure Project](https://gitlab.com/rychly-edu/projects/tarzan-docker-infrastructure)

## Acknowledgements

*This work was supported by the Ministry of the Interior of the Czech Republic as a part of the project Integrated platform for analysis of digital data from security incidents VI20172020062.*
