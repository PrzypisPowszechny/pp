FROM python:3.6-slim

# For apt related issues with interactions after installation
ENV DEBIAN_FRONTEND noninteractive

# postgresql-client is package required to open postgres cmdline, especially using manage.py dbshell.

# This distro has some over-optimization flows and some normal dirs are missing which causes errors.
# https://github.com/debuerreotype/debuerreotype/issues/10
RUN mkdir /usr/share/man/man1 && mkdir /usr/share/man/man7 \
 && apt-get update && apt-get install -y \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /var/cache/apt/*

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user
# Save bash history etc
VOLUME /home/user

RUN mkdir /code && chown user:user /code
WORKDIR /code

# Used by our entrypoint setting venv up
ENV VENV_PATH /opt/venv
RUN pip install --no-cache-dir virtualenv
# Own dir before making it a volume
RUN mkdir $VENV_PATH \
 && chown user:user -R $VENV_PATH
# Guarantees that pip correctly installs packages in venv even if user is root
ENV PIP_ROOT $VENV_PATH
ENV PIP_PREFIX=./

RUN pip install virtualenv \
 && virtualenv $VENV_PATH \
 && chown user:user -R $VENV_PATH

VOLUME $VENV_PATH
USER user

COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
