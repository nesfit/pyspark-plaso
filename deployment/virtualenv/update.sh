#!/bin/sh

# see https://github.com/qt/qtivi/tree/dev/src/3rdparty/virtualenv
# see https://github.com/pypa/virtualenv/issues/1549#issuecomment-588193632

URL="https://raw.githubusercontent.com/qt/qtivi/dev/src/3rdparty/virtualenv"

# download
wget -N "${URL}/relocate_virtualenv.py" "${URL}/VIRTUALENV_LICENSE"

# make shebang files executable
find . -type f ! -executable -exec sh -c "head -n 1 {} | grep -q '^#\!/' && chmod -v 755 {}" \;
