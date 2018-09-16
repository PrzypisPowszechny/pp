#!/usr/bin/env sh

echo Activating \"${ENV_PATH}\" virtualenv...

# Make sure all args given
if [ -z ${ENV_PATH} ]; then
    echo "virtualenv_entrypoint: Variable ENV_PATH for python virtual env is not defined!"
    return 1
fi

# Add here any commands that are required before starting python app
if ! [ -f ${ENV_PATH}/bin/activate ]
then
    pip install virtualenv
    virtualenv ${ENV_PATH}
fi

. ${ENV_PATH}/bin/activate
exec "$@"
