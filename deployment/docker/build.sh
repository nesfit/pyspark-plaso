#!/bin/sh

case "${1}" in
--build)
	ACTION_BUILD="Dockerfile"
	shift
	;;
--build=*)
	ACTION_BUILD="${1#*=}"
	shift
	;;
--pull)
	ACTION_PULL=1
	shift
	;;
--tag)
	ACTION_TAG=1
	shift
	;;
--push)
	ACTION_PUSH=1
	shift
	;;
--save=*)
	ACTION_SAVE="${1#*=}"
	shift
	;;
--*)
	echo "Wrong action '${1}'!" >&2
	exit 1
	;;
*)
	echo "Enabling '--build' action by default." >&2
	ACTION_BUILD=1
esac

IMAGE="${1}"; shift
TAG_FINAL="${1}"; shift
TAG_PREFIX="${1}"; shift
TAGS_FILE="${1:-docker-tags.txt}"; shift
TAGS=$(sed '/^#/d' "${TAGS_FILE}")

if [ -z "${IMAGE}" -o -z "${TAGS}" ]; then
	echo "Usage: ${0} [--build|--build=Dockerfile|--pull|--tag|--push] <image> [final-tag] [prefix] [tags-file] [docker-build-args ...]" >&2
	echo "Build/Pull/Push the Docker image (the first argument; there can be several space-separated images in this single argument) in several variants as defined in the file (the fourth argument)." >&2
	echo "Or Tag the first Docker image from space-separated images as the rest of the space-separated images in the first argument in several variants as defined in the file (the fourth argument)." >&2
	echo "The last of the variants will be tagged by the final tag (the second argument)." >&2
	echo "All the tags including the final tag will be prefixed by the prefix (the third argument) if defined." >&2
	echo "The rest of the arguments will be passed to the docker-build command." >&2
	echo "Error codes/exit values: 1 (wrong arguments), 2 (build or pull error), 3 (tag error), 4 (push error)" >&2
	exit 1
fi

## BUILD

if [ -n "${ACTION_BUILD}" ]; then

	IFS=$'\n'; for TAG in ${TAGS}; do
		TAG_NAME="${TAG_PREFIX}${TAG%%	*}"
		unset BUILD_ARGS
		IFS=" "; for BUILD_ARG in ${TAG#*	}; do
			BUILD_ARGS="${BUILD_ARGS} --build-arg=${BUILD_ARG}"
		done
		unset TAG_ARGS
		IFS=" "; for I in ${IMAGE}; do
			TAG_ARGS="${TAG_ARGS} --tag=${I}:${TAG_NAME}"
		done
		docker build "--file=${ACTION_BUILD}" ${BUILD_ARGS} --pull ${TAG_ARGS} $@ . || exit 2
	done

fi

## PULL

if [ -n "${ACTION_PULL}" ]; then

	IFS=$'\n'; for TAG in ${TAGS}; do
		TAG_NAME="${TAG_PREFIX}${TAG%%	*}"
		IFS=" "; for I in ${IMAGE}; do
			docker pull "${I}:${TAG_NAME}" || exit 2
		done
	done

fi

## TAG

if [ -n "${ACTION_TAG}" ]; then

	IFS=$'\n'; for TAG in ${TAGS}; do
		TAG_NAME="${TAG_PREFIX}${TAG%%	*}"
		FIRST_IMAGE="${IMAGE%% *}"
		IFS=" "; for I in ${IMAGE#* }; do
			docker tag "${FIRST_IMAGE}:${TAG_NAME}" "${I}:${TAG_NAME}" || exit 3
		done
	done

fi

if [ \( -n "${ACTION_BUILD}" -o -n "${ACTION_PULL}" -o -n "${ACTION_TAG}" \) -a -n "${TAG_FINAL}" ]; then

	TAG_FINAL="${TAG_PREFIX}${TAG_FINAL}"
	IFS=" "; for I in ${IMAGE}; do
		docker tag "${I}:${TAG_NAME}" "${I}:${TAG_FINAL}" || exit 3
	done

fi

## PUSH

if [ -n "${ACTION_PUSH}" ]; then

	IFS=$'\n'; for TAG in ${TAGS} ${TAG_FINAL}; do
		TAG_NAME="${TAG_PREFIX}${TAG%%	*}"
		IFS=" "; for I in ${IMAGE}; do
			docker push "${I}:${TAG_NAME}" || exit 4
		done
	done

fi

## SAVE

if [ -n "${ACTION_SAVE}" ]; then

	IFS=$'\n'; for TAG in ${TAGS}; do
		TAG_NAME="${TAG_PREFIX}${TAG%%	*}"
		IFS=" "; for I in ${IMAGE}; do
			FILE="${ACTION_SAVE}_${I##*/}_${TAG_NAME}.tar.gz"
			echo "Saving ${I}:${TAG_NAME} into file ${FILE} ..." >&2
			docker -l debug save "${I}:${TAG_NAME}" | gzip > "${FILE}"  || exit 5
		done
	done

	if [ -n "${I}" -a -n "${TAG_FINAL}" -a -n "${FILE}" ]; then
		FILE_FINAL="${ACTION_SAVE}_${I##*/}_${TAG_FINAL}.tar.gz"
		ln -vs "${FILE}" "${FILE_FINAL}"
	fi

fi
