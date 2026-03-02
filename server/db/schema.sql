CREATE TABLE member_eligibility (
    member_id TEXT PRIMARY KEY,
    plan_id TEXT,
    active_from DATE,
    active_to DATE,
    status TEXT
);

CREATE TABLE plan_coverage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT,
    cpt_code TEXT,
    covered TEXT
);

CREATE TABLE formulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT,
    drug_code TEXT,
    tier INTEGER,
    covered TEXT
);

CREATE TABLE medical_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpt_code TEXT,
    allowed_icd TEXT
);

CREATE TABLE claims_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT,
    drug_code TEXT,
    service_date DATE,
    npi TEXT
);

CREATE TABLE step_therapy_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_code TEXT,
    required_prior_drug TEXT
);

CREATE TABLE provider_registry (
    npi TEXT PRIMARY KEY,
    provider_name TEXT,
    status TEXT
);