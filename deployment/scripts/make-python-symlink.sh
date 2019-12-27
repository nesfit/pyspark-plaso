#!/bin/sh

SCRIPTNAME=$(readlink -f $0) DIRNAME=$(dirname ${SCRIPTNAME})/../build
mkdir -p "${DIRNAME}"

exec ln -vfs $(which python) "${DIRNAME}/python"
