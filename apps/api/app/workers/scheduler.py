from app.workers.broker import celery_app

celery_app.conf.beat_schedule = {}
