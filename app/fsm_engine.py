import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional, Tuple
import redis
from .config import settings
from .schemas import FSMState, FSMEvent, FSMTransitionResult


class FSMEngine:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.machines: Dict[str, Dict] = {}
        self._load_machines()

    def _load_machines(self):
        """FSM 정의 파일들을 로드합니다."""
        for filename in os.listdir(settings.fsm_definitions_path):
            if filename.endswith(".json"):
                machine_type = filename[:-5]  # .json 제외
                with open(os.path.join(settings.fsm_definitions_path, filename), encoding="utf-8") as f:
                    self.machines[machine_type] = json.load(f)

    def _get_state_key(self, machine_type: str, entity_id: str) -> str:
        """Redis 키를 생성합니다."""
        return f"fsm:{machine_type}:{entity_id}"

    def get_current_state(self, machine_type: str, entity_id: str) -> Optional[FSMState]:
        """현재 상태를 조회합니다."""
        state_data = self.redis_client.get(self._get_state_key(machine_type, entity_id))
        if not state_data:
            return None
        return FSMState.model_validate_json(state_data)

    def process_event(self, machine_type: str, entity_id: str, event: FSMEvent) -> FSMTransitionResult:
        """이벤트를 처리하고 상태를 전이합니다."""
        if machine_type not in self.machines:
            return FSMTransitionResult(success=False, current_state="", error_message=f"Unknown machine type: {machine_type}")

        current_state = self.get_current_state(machine_type, entity_id)
        machine_def = self.machines[machine_type]

        # 초기 상태 처리
        if not current_state:
            if "initial_state" not in machine_def:
                return FSMTransitionResult(success=False, current_state="", error_message="No initial state defined")
            current_state = FSMState(state=machine_def["initial_state"], entity_id=entity_id, machine_type=machine_type, metadata={}, updated_at=datetime.now(ZoneInfo("UTC")))

        # 전이 가능 여부 확인
        transitions = machine_def.get("transitions", {})
        if current_state.state not in transitions:
            return FSMTransitionResult(success=False, current_state=current_state.state, error_message=f"No transitions defined for state: {current_state.state}")

        allowed_events = transitions[current_state.state]
        if event.name not in allowed_events:
            return FSMTransitionResult(success=False, current_state=current_state.state, error_message=f"Event {event.name} not allowed in state {current_state.state}")

        # 상태 전이 수행
        new_state = allowed_events[event.name]
        previous_state = current_state.state

        current_state.state = new_state
        current_state.updated_at = datetime.now(ZoneInfo("UTC"))
        current_state.metadata.update(event.metadata)

        # Redis에 상태 저장
        self.redis_client.set(self._get_state_key(machine_type, entity_id), current_state.model_dump_json())

        return FSMTransitionResult(success=True, current_state=new_state, previous_state=previous_state)


fsm_engine = FSMEngine()
