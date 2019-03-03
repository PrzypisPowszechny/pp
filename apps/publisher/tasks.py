from worker import celery_app
from .demagog import sync_using_sources_list


@celery_app.task
def demagog_sync():
    sync_using_sources_list()


