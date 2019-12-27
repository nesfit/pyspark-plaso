#!/usr/bin/env bash

RELDIRNAME=$(dirname ${0}) DIRNAME=$(readlink -f ${RELDIRNAME})
BASENAME=${0##*/} SCRIPTNAME_WITHOUT_EXT="${BASENAME%.sh}"

# container names are in an appendix after _ or as args
DC_CONTAINER_NAME="${SCRIPTNAME_WITHOUT_EXT##*_}"
[[ "${DC_CONTAINER_NAME}" == "${SCRIPTNAME_WITHOUT_EXT}" ]] && DC_CONTAINER_NAME="${@}"

for I in `${DIRNAME}/run-docker-webapp.sh ps -q ${DC_CONTAINER_NAME}`; do
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${I}
done
