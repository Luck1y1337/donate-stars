from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backup import perform_backup


def start_scheduler(bot):
    """Создаёт и запускает планировщик фоновых задач (ночной авто-бэкап)."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        perform_backup,
        "cron",
        hour=3,
        minute=0,
        args=[bot],
        max_instances=1,
        misfire_grace_time=300,
    )
    scheduler.start()
    return scheduler
