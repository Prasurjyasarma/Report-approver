from pydantic import BaseModel
from typing import Optional

class ClaimInput(BaseModel):
    claim_id: Optional[str] = None
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    date_of_service: Optional[str] = None
    diagnosis_code: Optional[str] = None
    procedure_code: Optional[str] = None
    billed_amount: Optional[float] = None