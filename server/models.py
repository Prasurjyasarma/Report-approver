import os
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.orm import declarative_base, sessionmaker

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(CURRENT_DIR, "db", "insurance_engine.db")

print("Using DB:", db_path)

engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class MemberEligibility(Base):
    __tablename__ = "member_eligibility"

    member_id = Column(String, primary_key=True)
    plan_id = Column(String)
    active_from = Column(Date)
    active_to = Column(Date)
    status = Column(String)

class PlanCoverage(Base):
    __tablename__ = "plan_coverage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String)
    cpt_code = Column(String)
    covered = Column(String)

class Formulary(Base):
    __tablename__ = "formulary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String)
    drug_code = Column(String)
    tier = Column(Integer)
    covered = Column(String)

class MedicalRule(Base):
    __tablename__ = "medical_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cpt_code = Column(String)
    allowed_icd = Column(String)

class ClaimsHistory(Base):
    __tablename__ = "claims_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String)
    drug_code = Column(String)
    service_date = Column(Date)
    npi = Column(String)

class StepTherapyRule(Base):
    __tablename__ = "step_therapy_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_code = Column(String)
    required_prior_drug = Column(String)

class ProviderRegistry(Base):
    __tablename__ = "provider_registry"

    npi = Column(String, primary_key=True)
    provider_name = Column(String)
    status = Column(String)