# This inherits from ClaimInput

from pydantic import BaseModel
from typing import Optional
from models.claim_input import ClaimInput

class ClaimValidation(ClaimInput):
    # from RAG to fill 
    requires_auth: Optional[bool] = None
    is_covered: Optional[bool] = None
    fraud_indicators: Optional[list[str]] = None
    duplicate_check: Optional[bool] = None
    medical_necessity: Optional[bool] = None
    coding_valid: Optional[bool] = None