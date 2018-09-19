#!/usr/bin/env bash

# Make sure all args given
if [ -z ${ENV_PATH} ]; then
    echo "virtualenv_entrypoint: Variable ENV_PATH for python virtual env is not defined!"
    return 1
fi


if [ -f ${ENV_PATH}/bin/activate ]
then
    # Either activate env
    echo Activating \"${ENV_PATH}\" virtualenv...
    . ${ENV_PATH}/bin/activate
else
    # Or create env
    echo Creating \"${ENV_PATH}\" virtualenv...
    # We do not necessarily have to pip it, but this way this script can run with any python image
    pip install virtualenv
    virtualenv ${ENV_PATH}
    . ${ENV_PATH}/bin/activate

    # And install all proper requirements of our python app
    pip install  -r /code/requirements.txt
fi

exec "$@"