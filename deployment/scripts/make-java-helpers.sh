#!/bin/sh

set -e

SCRIPTNAME=$(readlink -f $0) DIRNAME=$(dirname ${SCRIPTNAME})/../build
mkdir -p "${DIRNAME}"

PYSPARK_HELPERS_DIR=${DIRNAME}/../../java-helpers

${PYSPARK_HELPERS_DIR}/build-deps.sh
${PYSPARK_HELPERS_DIR}/build.sh
cp -v ${PYSPARK_HELPERS_DIR}/build/libs/*.jar ${DIRNAME}/
