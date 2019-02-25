FROM python:3.6-slim

# For apt related issues with interactions after installation
ENV DEBIAN_FRONTEND noninteractive

# postgresql-client is package required to open postgres cmdline, especially using manage.py dbshell.

# This distro has some over-optimization flows, so for postgres we need to temporarly add man dirs.
# https://github.com/debuerreotype/debuerreotype/issues/10
RUN for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done \
 && apt-get update \
 && apt-get install -y \
    postgresql-client \
    gosu \
 && for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user
# Save bash history etc
VOLUME /home/user

# Used by our entrypoint setting venv up
ENV VENV_PATH /opt/venv
RUN pip install --no-cache-dir virtualenv

# Virtualenv will be probably ovveridden by mounted venv, but in case it is not, permissions are proper
RUN mkdir $VENV_PATH \
 && virtualenv $VENV_PATH \
 && chown user:user -R $VENV_PATH
VOLUME $VENV_PATH

# Mkdir only to set it as a workdir, it will be owned by user running container
RUN mkdir /code
WORKDIR /code

# Keep being root until switching to "user" with gosu in entrypoint
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
