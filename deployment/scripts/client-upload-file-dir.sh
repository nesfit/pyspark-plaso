#!/bin/sh

URL_DEFAULT="http://0.0.0.0:54380/"

if [ "${1:0:6}" = "--url=" ]; then
	URL="${1:6}"
	shift
else
	URL="${URL_DEFAULT}"
fi

if [ $# -lt 2 -o "${1}" = "--help" ]; then
	echo "${0} [--url=${URL_DEFAULT}] <path-where-to-upload> <file-or-directory-to-upload> [another-file-or-dir ...]" >&2
	exit 1
fi

function myzip() {
	if which 7z >/dev/null 2>&1; then
		7z a -mx $@
	elif which zip >/dev/null 2>&1; then
		zip -9r $@
	else
		echo "No application to create ZIP files!" >&2
		exit 1
	fi
}

function upload() {
	TO="${1}"
	FROM="${2}"
	if [ -d "${FROM}" ]; then
		# directory
		ZIP_DIR=$(mktemp -d)
		trap "{ rm -rf ${ZIP_DIR}; }" EXIT
		ZIP="${ZIP_DIR}/temp.zip"
		echo "### Packing ${FROM} directory into ZIP file ${ZIP}" >&2
		myzip "${ZIP}" "${FROM}"
		echo "### Uploading ZIP file ${ZIP} into ${TO}" >&2
		curl "${URL}zip/${TO}" --upload-file "${ZIP}"
		echo
	else
		# single file
		echo "### Uploading file ${FROM} into ${TO}" >&2
		curl "${URL}file/${TO}" --upload-file "${FROM}"
		echo
	fi
}

OUT="${1}"
shift

for I in $@; do
	upload "${OUT}" "${I}"
done
