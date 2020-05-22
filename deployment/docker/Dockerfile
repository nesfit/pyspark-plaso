# https://gitlab.com/rychly-edu/docker/docker-spark-app/container_registry
ARG FROM_TAG
FROM registry.gitlab.com/rychly-edu/docker/docker-spark-app:${FROM_TAG:-latest}

MAINTAINER Marek Rychly <marek.rychly@gmail.com>

ENV \
SPARK_JARS=/app/lib \
SPARK_PYFILES=/app/lib \
SPARK_APP=/app/webapp_main.py

RUN true \
# clean up a default app directory if any
&& rm -rf /app/* || true

# copy a new app diretory's contents
# if COPY's <src> is a directory, the directory itself is not copied, just its contents, so we need to copy into /app
COPY app /app/

EXPOSE 54380/tcp
