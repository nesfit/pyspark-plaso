#!/bin/sh

# Set client driver's opened ports from communicating with a Spark cluster (the port numbers must be allowed in the client's firewall)
# see https://spark.apache.org/docs/latest/configuration.html#networking
# * spark.driver.port used for communicating of the client driver with the executors and the standalone Master
SPARK_DRIVER_PORT=64001
# * spark.driver.blockManager.port used for providing an interface of the client driver's block manager for uploading and fetching blocks (i.e., a key-value store of blocks of data)
SPARK_DRIVER_BM_PORT=64017
# * spark.port.maxRetries to set a number of retries when binding to a port before giving up (each subsequent retry will increment the port used in the previous attempt by 1)
SPARK_PORT_MAX_RETRIES=16

# Set Python interpreter on both the driver/client and executors/workers
# see https://spark.apache.org/docs/latest/configuration.html#runtime-environment
# * spark.pyspark.driver.python to set Python binary executable to use for PySpark in driver
SPARK_PYTHON_DRIVER=python2
# * spark.pyspark.python to set Python binary executable to use for PySpark in executors (and also in the driver if spark.pyspark.driver.python unset)
SPARK_PYTHON_EXECUTORS=python2

# Spark Master node
# see docker-compose.yml
[[ -z "${SPARK_MASTER_HOST}" ]] && SPARK_MASTER_HOST=$(../scripts/get-docker-container-ip.sh sparkmaster)
[[ -z "${SPARK_MASTER_PORT}" ]] && SPARK_MASTER_PORT=7077
if [[ -n "${SPARK_MASTER_HOST}" ]]; then
	SPARK_MASTER="spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT}"
else
	SPARK_MASTER="local[*]"
	echo "Cannot detect an IP of the 'sparkmaster' node!" >&2
fi
echo "*** Using Spark master: ${SPARK_MASTER}"

JARS=$(ls ../build/*.jar | tr '\n' ',' | sed 's/,$//')
echo "*** Using JRSs: ${JARS}"

if [[ "${1}" = "shell" ]]; then
	shift
	PYTHONIOENCODING=utf8 exec pyspark \
	--conf spark.driver.port=${SPARK_DRIVER_PORT} \
	--conf spark.driver.blockManager.port=${SPARK_DRIVER_BM_PORT} \
	--conf spark.port.maxRetries=${SPARK_PORT_MAX_RETRIES} \
	--conf spark.pyspark.driver.python=${SPARK_PYTHON_DRIVER} \
	--conf spark.pyspark.python=${SPARK_PYTHON_EXECUTORS} \
	--master "${SPARK_MASTER}" \
	--jars "${JARS}" \
	$@
else
	SCRIPT="${1}"
	[[ -n "${SCRIPT}" ]] && shift || SCRIPT="${0%.sh}.py"
	PYTHONIOENCODING=utf8 exec spark-submit \
	--conf spark.driver.port=${SPARK_DRIVER_PORT} \
	--conf spark.driver.blockManager.port=${SPARK_DRIVER_BM_PORT} \
	--conf spark.port.maxRetries=${SPARK_PORT_MAX_RETRIES} \
	--conf spark.pyspark.driver.python=${SPARK_PYTHON_DRIVER} \
	--conf spark.pyspark.python=${SPARK_PYTHON_EXECUTORS} \
	--master "${SPARK_MASTER}" \
	--jars "${JARS}" \
	$@ "${SCRIPT}"
fi
