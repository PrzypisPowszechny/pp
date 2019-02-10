#!/usr/bin/env bash

echo "Env path: \"${VENV_PATH}\""

# Make sure all args given
if [ -z ${VENV_PATH} ]; then
    echo "virtualenv_entrypoint: Variable VENV_PATH for python virtual env is not defined!"
    return 1
fi

# Add here any commands that are required before starting python app
if ! [ -f ${VENV_PATH}/bin/activate ]
then
    echo Creating \"${VENV_PATH}\" virtualenv...
    # We do not necessarily have to pip it, but this way this script can run with any python image
    pip install virtualenv
    virtualenv ${VENV_PATH}
fi

echo Activating \"${VENV_PATH}\" virtualenv...
. ${VENV_PATH}/bin/activate

exec "$@"
