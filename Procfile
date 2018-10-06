web: gunicorn --log-level=info --access-logfile=- --error-logfile=- --config=python:wsgi wsgi
worker: celery worker --app=worker.celery_app --loglevel=info --concurrency=1  --beat
