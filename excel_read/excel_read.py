import os
import pandas as pd
from models.claim_input import ClaimInput

class ExcelRead:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), "Claims.xlsx")

    def get_claim_data(self) -> list[ClaimInput]:
        df = pd.read_excel(self.file_path)

        if df.empty:
            return []

        claims = []
        for _, row in df.iterrows():
            claim = ClaimInput(
                claim_id=str(row.get("claim_id")),
                patient_id=str(row.get("patient_id")),
                provider_id=str(row.get("provider_id")),
                date_of_service=str(row.get("date_of_service"))[:10],
                diagnosis_code=str(row.get("diagnosis_code")),
                procedure_code=str(row.get("procedure_code")),
                billed_amount=float(row.get("billed_amount")),
            )
            claims.append(claim)

        return claims