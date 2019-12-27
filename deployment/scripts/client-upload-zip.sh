#!/bin/sh

URL_DEFAULT="http://0.0.0.0:5432/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ $# -lt 2 -o "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] <path-where-to-upload> <zip-file-to-extract-there> [another-file-or-dir ...]" >&2
	exit 1
fi

function upload() {
	TO="${1}"
	FROM="${2}"
	echo "### Uploading ZIP file ${FROM} into ${TO}" >&2
	curl "${URL}zip/${TO}" --upload-file "${FROM}"
	echo
}

OUT="${1}"
shift

for I in $@; do
	upload "${OUT}" "${I}"
done
