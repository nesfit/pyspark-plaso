#!/bin/sh

[[ -z "${NAMENODE_HOST}" ]] && NAMENODE_HOST=$(./docker/docker-compose-ip.sh namenode)
[[ -z "${NAMENODE_PORT}" ]] && NAMENODE_PORT=8020

if [[ -z "${NAMENODE_HOST}" ]]; then
	NAMENODE="localhost"
	echo "Cannot detect an IP of the 'namenode' node! Using localhost." >&2
fi

HDFS="hdfs://${NAMENODE_HOST}:${NAMENODE_PORT}"
echo "*** Using HDFS: ${HDFS}"

DIR=../test_data

if [[ -z "${HADOOP_USER_NAME}" ]]; then
	export HADOOP_USER_NAME=hadoop
fi

# see https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#rmr
hadoop fs -rm -r "hdfs://${NAMENODE_HOST}:${NAMENODE_PORT}/${DIR##*/}"

# see https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#copyFromLocal
hadoop fs -copyFromLocal -f "${DIR}" "hdfs://${NAMENODE_HOST}:${NAMENODE_PORT}/"

# see https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#lsr
hadoop fs -ls -R "hdfs://${NAMENODE_HOST}:${NAMENODE_PORT}/${DIR##*/}"
