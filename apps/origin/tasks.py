from worker import celery_app


@celery_app.task
def sync_with_demagog():
    from .demagog_consumer import consume_statements_from_sources_list
    consume_statements_from_sources_list()
