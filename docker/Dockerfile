FROM python:3.6-slim

RUN mkdir /code
WORKDIR /code

RUN pip install --no-cache-dir virtualenv
VOLUME /opt/venv

# Save bash history etc
VOLUME /root

# Used by our entrypoint setting venv up
ENV VENV_PATH /opt/venv

# Guarantees that pip correctly installs packages in venv even if user is root
ENV PIP_ROOT /opt/venv/
ENV PIP_PREFIX=./

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


COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
