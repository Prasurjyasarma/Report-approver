from server.models import (
    SessionLocal, MemberEligibility, PlanCoverage, Formulary,
    MedicalRule, ClaimsHistory, StepTherapyRule, ProviderRegistry
)

class Queries:
    def __init__(self):
        self.db = SessionLocal()

    def get_member_eligibility(self, member_id):
        return self.db.query(MemberEligibility).filter(
            MemberEligibility.member_id == member_id
        ).first()

    def get_plan_coverage(self, plan_id):
        return self.db.query(PlanCoverage).filter(
            PlanCoverage.plan_id == plan_id
        ).all()

    def get_formulary(self, plan_id):
        return self.db.query(Formulary).filter(
            Formulary.plan_id == plan_id
        ).all()

    def get_medical_rule(self, cpt_code):
        return self.db.query(MedicalRule).filter(
            MedicalRule.cpt_code == cpt_code
        ).first()

    def get_claims_history(self, member_id):
        return self.db.query(ClaimsHistory).filter(
            ClaimsHistory.member_id == member_id
        ).all()

    def get_step_therapy_rule(self, drug_code):
        return self.db.query(StepTherapyRule).filter(
            StepTherapyRule.drug_code == drug_code
        ).first()

    def get_provider_registry(self, npi):
        return self.db.query(ProviderRegistry).filter(
            ProviderRegistry.npi == npi
        ).first()