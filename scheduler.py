import sqlite3
from datetime import timedelta

from celery import Celery, platforms
from celery.schedules import crontab

from config import Config
from main import Detector

platforms.C_FORCE_ROOT = True
celery_db = f"{Config.name}_scheduler.db"
sqlite3.connect(celery_db)
app_run = Celery(Config.name, broker=f"sqla+sqlite:///{celery_db}")

app_run.conf.update(
    beat_schedule={
        "定时检测": {
            "task": "scheduler.run_check",
            # "schedule": crontab(hour=9, minute=00),
            "schedule": timedelta(seconds=60),
        }
    }
)


@app_run.task()
def run_check():
    Detector().get_data()
