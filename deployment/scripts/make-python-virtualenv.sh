#!/bin/sh

set -e

SCRIPTNAME=$(readlink -f $0) DIRNAME=$(dirname ${SCRIPTNAME})/../build
mkdir -p "${DIRNAME}"

VENV_NAME="${1:-${DIRNAME}/venv}"

if [[ -e "${VENV_NAME}" ]]; then
	echo "VirtualEnv Directory ${VENV_NAME} already exists! Removing!" >&2
	rm -rf "${VENV_NAME}" && echo "The old VirtualEnv Directory ${VENV_NAME} removed."
fi

echo "Creating VirtualEnv directory ${VENV_NAME}" >&2
# use python from PATH as with the symlink in ./build, python thinks sys.prefix is wrong
virtualenv --clear --python=python "${VENV_NAME}"
virtualenv --relocatable "${VENV_NAME}"

echo "Installing required Python packages into VirtualEnv directory ${VENV_NAME}" >&2
source "${VENV_NAME}/bin/activate"
pip install --ignore-installed --requirement ${DIRNAME}/../../misc/dependencies.txt
