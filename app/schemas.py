from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class FSMEvent(BaseModel):
    name: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class FSMState(BaseModel):
    state: str
    entity_id: str
    machine_type: str
    metadata: Dict[str, Any] = {}
    updated_at: datetime


class FSMTransitionResult(BaseModel):
    success: bool
    current_state: str
    previous_state: Optional[str] = None
    error_message: Optional[str] = None
