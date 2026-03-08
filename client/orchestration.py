import json
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from excel_read.excel_read import ExcelRead
from models.claim_input import ClaimInput
from models.claim_validation import ClaimValidation
from models.claim_result import ClaimResult
from Rag.rag import PolicyRAG
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from client.system_prompt import SystemPrompt

load_dotenv()

# Shared state that flows through the graph gets data from pydentic model


class ClaimState(TypedDict):
    claims: list[dict]
    validated_claims: list[dict]
    claim_results: list[dict]


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
        AUTH_REQUIRED_PROCEDURES = {"97110"}
        requires_auth = claim.procedure_code in AUTH_REQUIRED_PROCEDURES
        is_covered = any("covered" in r.lower() for r in coverage_results)

        fraud_indicators = []

        # High billed amount
        if claim.billed_amount > 500:
            fraud_indicators.append("High billed amount")

        # repeated procedure for same patient
        repeat_count = sum(
            1 for c in state["claims"]
            if c["patient_id"] == claim.patient_id
            and c["procedure_code"] == claim.procedure_code
        )
        if repeat_count > 1:
            fraud_indicators.append("Potential repeated procedure")

        duplicate_check = any(
            c["patient_id"] == claim.patient_id and
            c["procedure_code"] == claim.procedure_code and
            c["date_of_service"] == claim.date_of_service and
            c["claim_id"] != claim.claim_id
            for c in state["claims"]
        )
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


# Node 3 - Pass validated claims to LLM
def llm_processing_node(state: ClaimState) -> ClaimState:
    llm = AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    claim_results = []

    for claim_data in state["validated_claims"]:
        # Validation against pydentic rules
        validated = ClaimValidation(**claim_data)

        messages = [
            SystemMessage(content=SystemPrompt.CLAIMS_ADJUDICATOR),
            HumanMessage(
                content=f"Adjudicate this claim:\n{validated.model_dump_json(indent=2)}"),
        ]

        response = llm.invoke(messages)

        try:
            result_json = json.loads(response.content)
            result = ClaimResult(**result_json)

        except (json.JSONDecodeError, Exception) as e:
            print(f"LLM response parse error for {validated.claim_id}: {e}")
            result = ClaimResult(
                claim_id=validated.claim_id,
                decision="PENDING",
                reason="LLM response could not be parsed",
                flags=["parse_error"],
                confidence=0.0,
            )
        claim_results.append(result.model_dump())

    print(f"Processed {len(claim_results)} claim(s) through LLM.")
    return {"claim_results": claim_results}


# MAIN Graph
def build_graph():
    graph = StateGraph(ClaimState)

    # nodes
    graph.add_node("read_excel", read_excel_node)
    graph.add_node("rag_validation", rag_validation_node)
    graph.add_node("llm_processing", llm_processing_node)

    # edges
    graph.add_edge(START, "read_excel")
    graph.add_edge("read_excel", "rag_validation")
    graph.add_edge("rag_validation", "llm_processing")
    graph.add_edge("llm_processing", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "claims": [],
        "validated_claims": [],
        "claim_results": [],
    })

    print("\n=== Claim Results ===\n")
    for r in result["claim_results"]:
        claim_result = ClaimResult(**r)
        print(claim_result.model_dump_json(indent=2))
        print("---")
