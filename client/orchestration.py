from server.server import get_member_eligibility
from client.excel_read.excel_read import ExcelRead
from client.claim_state import ClaimState


# Node 1
def read_excel_node(state: ClaimState) -> ClaimState:
    reader = ExcelRead()
    data = reader.get_claim_data()

    if data["member_id"] == "NOT_FOUND":
        state.eligibility_status = "DENY"
        return state

    state.member_id = data["member_id"]
    return state

# Node 2
def eligibility_node(state: ClaimState) -> ClaimState:
    response = get_member_eligibility(state.member_id)

    if response["status"] == "NOT_FOUND":
        state.eligibility_status = "DENY"
        return state

    if response["status"] != "ACTIVE":
        state.eligibility_status = "DENY"
        return state

    state.plan_id = response["plan_id"]
    state.coverage_start = response["active_from"]
    state.coverage_end = response["active_to"]
    state.eligibility_status = "PASS"

    return state



if __name__ == "__main__":
    state = ClaimState(member_id=None)
    state = read_excel_node(state)
    state = eligibility_node(state)

    print(state.model_dump())