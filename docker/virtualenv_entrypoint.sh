#!/usr/bin/env bash

echo "Env path: \"${ENV_PATH}\""

# Make sure all args given
if [ -z ${ENV_PATH} ]; then
    echo "virtualenv_entrypoint: Variable ENV_PATH for python virtual env is not defined!"
    return 1
fi

# Add here any commands that are required before starting python app
if ! [ -f ${ENV_PATH}/bin/activate ]
then
    echo "Creating virtualenv..."
    # We do not necessarily have to pip it, but this way this script can run with any python image
    pip install virtualenv
    virtualenv ${ENV_PATH}
fi

echo "Activating virtualenv..."
. ${ENV_PATH}/bin/activate

exec "$@"
