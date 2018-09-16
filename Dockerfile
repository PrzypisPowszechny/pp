FROM python:3.6-alpine
ADD ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN apk update && apk add --virtual .build-deps gcc musl-dev python3-dev && apk add postgresql-dev && \
    \
    pip install --no-cache-dir -r requirements.txt && \
    \
    apk del .build-deps
VOLUME /usr/local/lib/python3.6/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
