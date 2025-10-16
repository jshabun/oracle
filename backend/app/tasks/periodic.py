from .celery_app import app

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Every 15 minutes: pull league transactions, injuries, etc.
    sender.add_periodic_task(15*60, sync_all_leagues.s(), name="sync leagues")