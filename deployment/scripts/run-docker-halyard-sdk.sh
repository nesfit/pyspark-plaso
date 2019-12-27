#!/bin/sh

RELDIRNAME=$(dirname ${0}) DIRNAME=$(readlink -f ${RELDIRNAME})

exec docker run --rm -ti \
	--network docker_default \
	--env ZOO_SERVERS=zookeeper \
	--env ZOO_PORT=2181 \
	--env ROOT_DIR="hdfs://namenode:8020/user/hbase" \
	registry.gitlab.com/rychly-edu/docker/docker-halyard-sdk
