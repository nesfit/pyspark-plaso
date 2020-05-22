#!/bin/sh

SCRIPTNAME=$(readlink -f $0) DIRNAME=$(dirname ${SCRIPTNAME})

DC_FILE="${DIRNAME}/../docker-compose/webapp.yml"
DC_DIR=$(dirname ${DC_FILE})
DOCKER_COMPOSE="docker-compose -f ${DC_FILE} -p pyspark-plaso-webapp"

if [ $# -lt 1 ]; then
	grep -o '\./volumes/[^:]*' "${DC_FILE}" | ( cd "${DC_DIR}" && xargs mkdir -vp )
	mkdir -p "${DC_DIR}/volumes/app/lib"
	cp -v ${DIRNAME}/../build/*.zip ${DIRNAME}/../build/*.jar "${DC_DIR}/volumes/app/lib/"
	cp -rv ${DIRNAME}/../src/* "${DC_DIR}/volumes/app/"
	${DOCKER_COMPOSE} down
	exec ${DOCKER_COMPOSE} up
else
	exec ${DOCKER_COMPOSE} $@
fi
