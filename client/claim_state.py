from pydantic import BaseModel
from typing import Optional

class ClaimState(BaseModel):
    member_id: Optional[str] = None
    plan_id: Optional[str] = None
    eligibility_status: Optional[str] = None
    coverage_start: Optional[str] = None
    coverage_end: Optional[str] = None