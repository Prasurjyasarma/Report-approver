from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClaimResult(BaseModel):
    claim_id: Optional[str] = None
    decision: Optional[str] = None        # APPROVED / REJECTED / PENDING / FLAGGED
    reason: Optional[str] = None
    flags: Optional[list[str]] = None
    confidence: Optional[float] = None
    processed_at: datetime = datetime.now()