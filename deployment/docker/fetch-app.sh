#!/bin/sh

set -e

DIR=..
DIR_BUILD="${DIR}/build"
DIR_BUILD_JH="${DIR}/../java-helpers/build/libs"
DIR_SRC="${DIR}/src"

OUT=./app

# build by
if [ "${1}" = "--build" ]; then
	cd "${DIR}"
	./010-make-python-virtualenv.sh
	./020-make-site-packages-zip.sh
	./030-make-java-helpers.sh
	DIR_BUILD_JH="${DIR_BUILD}"
	cd -
fi

# move application
mkdir -vp "${OUT}/lib"
cp -v ${DIR_BUILD}/*.zip ${DIR_BUILD_JH}/*.jar "${OUT}/lib/"
cp -vr ${DIR_SRC}/* "${OUT}/"
