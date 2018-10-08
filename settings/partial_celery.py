import os

# Url like this: 'redis://redis:6379/'
from celery.schedules import crontab

BROKER_URL = os.environ.get('REDIS_URL')

CELERY_MAX_TASKS_PER_CHILD = 1000

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

CELERY_TIMEZONE = 'Europe/Warsaw'
CELERY_ENABLE_UTC = True
CELERY_IGNORE_RESULT = True

CELERY_DEFAULT_QUEUE = 'general'
CELERY_DEFAULT_EXCHANGE = 'general'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'general'


CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s][%(process)s][%(name)s] %(message)s"
CELERYD_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s][%(process)s][%(name)s] " \
                          "[%(task_name)s(%(task_id)s)] %(message)s"


CELERYBEAT_SCHEDULE = {
    'sync_with_demagog': {
        'task':
            'apps.publisher.demagog.sync_using_sources_list',
        'schedule': crontab(minute='*/15'),
    },
}
