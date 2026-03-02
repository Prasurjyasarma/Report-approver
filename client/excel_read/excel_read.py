import pandas as pd
import openpyxl

class ExcelRead:
    def __init__(self):
        self.file_path = "/Users/prasurjyasarma/Developer/report-approver/client/excel_read/claims.xlsx"

    def get_claim_data(self):
        df = pd.read_excel(self.file_path)

        if df.empty:
            return {"member_id": "NOT_FOUND"}

        return {
            "member_id": df.loc[0, "member_id"]
        }