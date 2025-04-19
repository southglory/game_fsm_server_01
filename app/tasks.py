from celery import Celery
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from .config import settings

celery_app = Celery("fsm_tasks", broker=settings.redis_url)


@celery_app.task(bind=True, max_retries=3)
def log_transition(self, machine_type: str, entity_id: str, from_state: str, to_state: str, event_name: str, metadata: dict):
    """상태 전이를 로깅하는 Celery 태스크"""
    try:
        log_entry = {
            "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
            "machine_type": machine_type,
            "entity_id": entity_id,
            "from_state": from_state,
            "to_state": to_state,
            "event_name": event_name,
            "metadata": metadata,
        }

        # 실제 프로덕션에서는 로그를 데이터베이스나 로그 시스템에 저장
        print(f"FSM Transition Log: {json.dumps(log_entry, indent=2)}")
        return True
    except Exception as exc:
        self.retry(exc=exc, countdown=2**self.request.retries)
