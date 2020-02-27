#!/bin/sh

PLASO_REPO="https://github.com/log2timeline/plaso.git"
PLASO_BRANCH=20200227
PLASO_DIR="test_data"

PLASO_GIT=$(mktemp -d plaso-XXXXXXXXXX.git || echo /tmp/plaso-$$.git)
trap "{ rm -rf ${PLASO_GIT}; }" EXIT

PLASO_ZIP="./test_data/plaso/${PLASO_BRANCH}.zip"
mkdir -p "${PLASO_ZIP%/*}"

echo "# cloning ${PLASO_REPO} ..." >&2
git clone --bare --depth=1 "--branch=${PLASO_BRANCH}" "${PLASO_REPO}" "${PLASO_GIT}"

echo "# zipping ${PLASO_DIR} into ${PLASO_ZIP} ..." >&2
git "--git-dir=${PLASO_GIT}" archive --format=zip "${PLASO_BRANCH}" "${PLASO_DIR}" > "${PLASO_ZIP}" \
&& ls -l "${PLASO_ZIP}" \
&& echo "# done" >&2
