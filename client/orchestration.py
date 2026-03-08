from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from excel_read.excel_read import ExcelRead
from models.claim_input import ClaimInput
from models.claim_validation import ClaimValidation
from Rag.rag import PolicyRAG


#Shared state that flows through the graph gets data from pydentic model
class ClaimState(TypedDict):
    claims: list[dict]               
    validated_claims: list[dict]    


# Node 1 - Read claims from Excel
def read_excel_node(state: ClaimState) -> ClaimState:
    reader = ExcelRead()
    claims = reader.get_claim_data()

    if not claims:
        print("No claims found in Excel file.")
        return {"claims": [], "validated_claims": []}
    print(f"Loaded {len(claims)} claim(s) from Excel.")
    return {"claims": [c.model_dump() for c in claims]}


# Node 2 - Validate each claim against policy rules using RAG
def rag_validation_node(state: ClaimState) -> ClaimState:
    rag = PolicyRAG()
    validated_claims = []

    for claim_data in state["claims"]:
        claim = ClaimInput(**claim_data)

        auth_results = rag.query(
            f"Does procedure code {claim.procedure_code} require prior authorization?",
            n_results=2,
        )
        coverage_results = rag.query(
            f"Is procedure {claim.procedure_code} covered under insurance plan?",
            n_results=2,
        )
        fraud_results = rag.query(
            f"What are fraud indicators for a ${claim.billed_amount} claim?",
            n_results=2,
        )
        duplicate_results = rag.query(
            f"How to detect duplicate claims for patient {claim.patient_id} "
            f"with procedure {claim.procedure_code} on {claim.date_of_service}?",
            n_results=2,
        )
        necessity_results = rag.query(
            f"Is procedure {claim.procedure_code} medically necessary "
            f"for diagnosis {claim.diagnosis_code}?",
            n_results=2,
        )
        coding_results = rag.query(
            f"Is diagnosis code {claim.diagnosis_code} and procedure code "
            f"{claim.procedure_code} valid under ICD-10 and CPT?",
            n_results=2,
        )

        requires_auth = any("authorization" in r.lower() for r in auth_results)
        is_covered = any("covered" in r.lower() for r in coverage_results)

        fraud_indicators = []
        for r in fraud_results:
            if "unusually high" in r.lower() and claim.billed_amount > 500:
                fraud_indicators.append("High billed amount")
            if "repeated procedures" in r.lower():
                fraud_indicators.append("Potential repeated procedure")

        duplicate_check = any("duplicate" in r.lower() for r in duplicate_results)
        medical_necessity = any(
            "medically necessary" in r.lower() or "medical necessity" in r.lower()
            for r in necessity_results
        )
        coding_valid = any(
            "icd" in r.lower() or "cpt" in r.lower() for r in coding_results
        )

        validated = ClaimValidation(
            **claim.model_dump(),
            requires_auth=requires_auth,
            is_covered=is_covered,
            fraud_indicators=fraud_indicators if fraud_indicators else None,
            duplicate_check=duplicate_check,
            medical_necessity=medical_necessity,
            coding_valid=coding_valid,
        )
        validated_claims.append(validated.model_dump())

    print(f"Validated {len(validated_claims)} claim(s) using policy RAG.")
    return {"validated_claims": validated_claims}




# MAIN Graph
def build_graph():
    graph = StateGraph(ClaimState)

    #nodes
    graph.add_node("read_excel", read_excel_node)
    graph.add_node("rag_validation", rag_validation_node)
  
    #edges
    graph.add_edge(START, "read_excel")
    graph.add_edge("read_excel", "rag_validation")
    graph.add_edge("rag_validation", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "claims": [],
        "validated_claims": [],
    })

    print("\n=== Validated Claims ===\n")
    for v in result["validated_claims"]:
        validated = ClaimValidation(**v)
        print(validated.model_dump_json(indent=2))
        print("---")