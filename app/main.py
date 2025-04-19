from fastapi import FastAPI, HTTPException
from typing import Optional, List
import os
import json
from .schemas import FSMEvent, FSMState, FSMTransitionResult
from .fsm_engine import fsm_engine
from .tasks import log_transition
from .config import settings

app = FastAPI(title="FSM Processing Server")


@app.get("/fsm/machines", response_model=List[str])
async def list_machines():
    """사용 가능한 FSM 타입 목록을 반환합니다."""
    return list(fsm_engine.machines.keys())


@app.get("/fsm/machines/{machine_type}")
async def get_machine_definition(machine_type: str):
    """특정 FSM의 정의를 반환합니다."""
    if machine_type not in fsm_engine.machines:
        raise HTTPException(status_code=404, detail="Machine type not found")
    return fsm_engine.machines[machine_type]


@app.get("/fsm/machines/{machine_type}/entities/{entity_id}", response_model=Optional[FSMState])
async def get_entity_state(machine_type: str, entity_id: str):
    """특정 엔티티의 현재 상태를 조회합니다."""
    state = fsm_engine.get_current_state(machine_type, entity_id)
    if not state:
        raise HTTPException(status_code=404, detail="Entity state not found")
    return state


@app.post("/fsm/machines/{machine_type}/entities/{entity_id}/events", response_model=FSMTransitionResult)
async def process_event(machine_type: str, entity_id: str, event: FSMEvent):
    """이벤트를 처리하고 상태를 전이합니다."""
    current_state = fsm_engine.get_current_state(machine_type, entity_id)
    previous_state = current_state.state if current_state else None

    result = fsm_engine.process_event(machine_type, entity_id, event)

    if result.success:
        # 비동기로 로그 기록
        log_transition.delay(machine_type=machine_type, entity_id=entity_id, from_state=previous_state, to_state=result.current_state, event_name=event.name, metadata=event.metadata)

    return result
