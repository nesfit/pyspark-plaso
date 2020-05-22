#!/bin/sh

URL_DEFAULT="http://0.0.0.0:54380/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ $# -lt 2 -o "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] <path-where-to-download> <file-path-to-download> [another-file ...]" >&2
	exit 1
fi

function download() {
	TO="${1}"
	FROM="${2}"
	echo "### Downloading file ${FROM} into ${TO}" >&2
	#wget --content-disposition -P "${TO}" "${URL}api/file/${FROM}"
	# curl: the first try to download and detect an error, the second try get the error message
	( cd "${TO}" && curl --fail -OJ "${URL}api/file/${FROM}" || curl "${URL}api/file/${FROM}" )
	echo
}

OUT="${1}"
shift

for I in $@; do
	download "${OUT}" "${I}"
done
