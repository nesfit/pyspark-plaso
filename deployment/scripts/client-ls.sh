#!/bin/sh

URL_DEFAULT="http://0.0.0.0:54380/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] [path-to-list] [another-path ...]" >&2
	exit 1
fi

function list() {
	FROM="${1}"
	echo "### Listing ${FROM}" >&2
	curl "${URL}ls/${FROM}"
	echo
}

for I in ${@:-.}; do
	list "${I}"
done
