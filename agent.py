from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from services.jobs_service import JobService
from datetime import datetime, timedelta
from utils.logger import logger


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BlockingScheduler(jobstores=jobstores)

agent_job = JobService()

# Schedule pipeline runs every 2 weeks
scheduler.add_job(
    agent_job.run_all_pipelines,
    trigger="interval",
    weeks=2,
    next_run_time=datetime.now() + timedelta(seconds=10),
    id="full_pipeline_sequence",
    replace_existing=True
)

# Schedule cleanup every 2 weeks
scheduler.add_job(
    agent_job.safe_run(agent_job.cleanup_curated_data),
    trigger="interval",
    weeks=2,
    next_run_time=datetime.now() + timedelta(days=1),
    id="cleanup_curated_data",
    replace_existing=True
)

logger.info("Agent starting. Scheduler is now running...")
scheduler.start()
