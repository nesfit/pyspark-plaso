#!/bin/sh

URL_DEFAULT="http://0.0.0.0:54380/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] [path-to-extract] [another-path ...]" >&2
	exit 1
fi

function extract() {
	FROM="${1}"
	echo "### Extracting ${FROM}" >&2
	curl "${URL}api/extract/${FROM}"
	echo
}

for I in ${@:-.}; do
	extract "${I}"
done
