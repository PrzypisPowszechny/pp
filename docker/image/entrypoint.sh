#!/usr/bin/env bash

set -e

if [ -z ${VENV_PATH} ]; then
    echo "Variable ENV_PATH for python virtual env is not defined! It should be set in docker image"
    return 1
fi

# get uid/gid of repo owner (external user)
EXTERNAL_UID=$(ls -nd /code | cut -f3 -d' ')
EXTERNAL_GID=$(ls -nd /code | cut -f4 -d' ')

if [ ! -z "$EXTERNAL_UID" -a ! -z "$EXTERNAL_GID" ]; then
    # get the uid/gid of docker "user"
    INTERNAL_UID=$(getent passwd user | cut -f3 -d: || true)
    INTERNAL_GID=$(getent group user | cut -f3 -d: || true)

    echo "Your user's (repo's dir owner) uid:gid==${EXTERNAL_UID}:${EXTERNAL_GID}," \
          "internal uid:gid==${INTERNAL_UID}:${INTERNAL_GID}"

    if [ "$EXTERNAL_GID" != "$INTERNAL_GID" ] || [ "$EXTERNAL_UID" != "$INTERNAL_UID" ]; then
        if [ "$(ls -nd /home/user | cut -f3 -d' ')" != "$EXTERNAL_UID" ]; then
            echo "Updating files ownership from ${INTERNAL_UID}:${INTERNAL_GID} to ${EXTERNAL_UID}:${EXTERNAL_GID}"
            find / -mount -uid ${INTERNAL_UID} -exec chown ${EXTERNAL_UID}:${EXTERNAL_GID} {} \;
        fi

        echo "Updating internal uid:gid to ${EXTERNAL_UID}:${EXTERNAL_GID}"
        usermod -u ${EXTERNAL_UID} user
        groupmod -g ${EXTERNAL_GID} user
    fi

    VENV_OWNER_UID=$(ls -nd ${VENV_PATH} | cut -f3 -d' ')
    if [ "$VENV_OWNER_UID" == "0" ]; then
       echo "Updating venv ownership from root to ${EXTERNAL_UID}"
       chown ${EXTERNAL_UID}:${EXTERNAL_GID} ${VENV_PATH}
    fi
fi

if ! [ -f ${VENV_PATH}/bin/activate ]
then
    echo "Creating virtualenv..."
    gosu user virtualenv ${VENV_PATH}
fi

set +e

NESTED_CMD="$@"
echo Activating \"${VENV_PATH}\" virtualenv...
exec gosu user bash -c  "
    . ${VENV_PATH}/bin/activate;
    echo Activated;
    echo Executing ${NESTED_CMD}...;
    ${NESTED_CMD}
"
