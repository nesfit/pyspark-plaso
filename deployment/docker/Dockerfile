# https://gitlab.com/rychly-edu/docker/docker-spark-app/container_registry
ARG FROM_TAG
FROM registry.gitlab.com/rychly-edu/docker/docker-spark-app:${FROM_TAG:-latest}

MAINTAINER Marek Rychly <marek.rychly@gmail.com>

ENV \
SPARK_JARS=/app/lib \
SPARK_PYFILES=/app/lib \
SPARK_APP=/app/webapp_main.py

COPY app /

EXPOSE 54380/tcp
