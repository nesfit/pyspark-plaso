#!/bin/sh

set -e

SCRIPTNAME=$(readlink -f $0) DIRNAME=$(dirname ${SCRIPTNAME})

WEBAPP_DIR="${DIRNAME}/../docker-compose/volumes/app"

mkdir -p "${WEBAPP_DIR}/lib"
cp -v ${DIRNAME}/../build/*.zip ${DIRNAME}/../build/*.jar "${WEBAPP_DIR}/lib/"
cp -rv ${DIRNAME}/../src/* "${DIRNAME}/../docker-compose/volumes/app/"

exec ${DIRNAME}/run-docker-webapp.sh restart sparkapp
