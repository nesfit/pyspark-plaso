# shell environment variables that should be available before running anything

# set a temporary directory for derby.log and metastore_db created by PySpark
export _JAVA_OPTIONS="-Dderby.system.home=.derby ${_JAVA_OPTIONS}"

# set current SOURCE_DATE_EPOCH to prevent "ZIP does not support timestamps before 1980" when using pythonPackages.wheel, see https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md#python-setuppy-bdist_wheel-cannot-create-whl
export SOURCE_DATE_EPOCH=$(date +%s)

## Python options
#export PYTHONDEBUG=0
#export PYTHONVERBOSE=0
# to prevent UnicodeEncodeError: 'ascii' codec can't encode character u'...
export PYTHONIOENCODING=utf8

# DO NOT USE THE FOLLOWING WITH VIRTUALENV (it installs pip into a virtualenv-incompatible directory)
# install Pip packages into a local subdirectory _build and Python should use them (it is necessary because the Python installation lives inside the read-only Nix store and pip would not be able to install packages there)
#export PYTHONVERSION="$(python -V | grep -om 1 '[[:digit:]]\+\.[[:digit:]]\+')"
#export PIP_PREFIX="$(pwd)/_build/pip_packages"
#export PYTHONPATH="$(pwd)/_build/pip_packages/lib/python$PYTHONVERSION/site-packages:$PYTHONPATH"
