from __future__ import annotations
import traceback
from loguru import logger
from .config import load_settings
from .db import make_engine
from .opslog import start_run, mark_success, mark_error
from .pipeline import fetch_from_production, transform_data, write_to_report
from .notify import send_email

def run() -> None:
    settings = load_settings()
    logger.info("Starting core-runner")

    prod_engine = make_engine(settings.prod_db_url)
    report_engine = make_engine(settings.report_db_url)
    opslog_engine = make_engine(settings.opslog_db_url)

    run_id = start_run(
        opslog_engine,
        run_id=settings.run_id,
        component="core-runner",
        trigger=settings.run_trigger,
        source=settings.run_source,
        meta={"version": "0.1.0"}
    )
    logger.bind(run_id=run_id).info(f"Run started: {run_id}")

    try:
        records = fetch_from_production(prod_engine)
        processed = transform_data(records)
        written = write_to_report(report_engine, processed)

        mark_success(opslog_engine, run_id=run_id, meta={"input": len(records), "written": written})
        logger.info(f"Run success: {run_id} (input={len(records)}, written={written})")

    except Exception as e:
        stack = traceback.format_exc()
        mark_error(opslog_engine, run_id=run_id, error_message=str(e), error_stack=stack)
        logger.error(f"Run error: {run_id} - {e}\n{stack}")

        # Optional email notification
        if settings.notify_email_to and settings.notify_email_from and settings.smtp_host:
            try:
                recipients = [s.strip() for s in settings.notify_email_to.split(",") if s.strip()]
                send_email(
                    host=settings.smtp_host,
                    port=settings.smtp_port,
                    user=settings.smtp_user,
                    password=settings.smtp_password,
                    use_tls=settings.smtp_use_tls,
                    sender=settings.notify_email_from,
                    recipients=recipients,
                    subject=f"[core-runner] ERROR run_id={run_id}",
                    body=f"""An error occurred during core-runner execution.

run_id: {run_id}
error : {e}
stack :

{stack}
"""
                )
                logger.info("Error notification sent")
            except Exception as e2:
                logger.error(f"Failed to send error notification: {e2}")
        raise  # ensure container exits non-zero

if __name__ == "__main__":
    run()
