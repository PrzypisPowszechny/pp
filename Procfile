web: gunicorn wsgi
worker: celery worker --app=worker.celery_app --loglevel=info --concurrency=1  --beat
