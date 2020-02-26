#!/bin/sh

URL_DEFAULT="http://0.0.0.0:54380/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ $# -lt 1 -o "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] <path-remove> [another-path ...]" >&2
	exit 1
fi

function remove() {
	FROM="${1}"
	echo "### Removing ${FROM}" >&2
	curl "${URL}rm/${FROM}"
	echo
}

for I in ${@}; do
	remove "${I}"
done
