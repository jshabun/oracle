from .celery_app import app

@app.task
def sync_all_leagues():
    # TODO: iterate users/leagues and refresh caches
    return {"synced": True}