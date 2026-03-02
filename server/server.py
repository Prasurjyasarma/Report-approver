from server.queries import Queries
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
query = Queries()

# get member eligibility
@mcp.tool()
def get_member_eligibility(member_id: str) -> dict:
    """
    Retrieve eligibility details for a health insurance member.

    This tool fetches membership information associated with the given member ID,
    including plan enrollment status and active coverage period.

    Use this tool to determine whether a member exists in the system and retrieve
    their insurance plan details before performing eligibility or coverage checks.

    Args:
        member_id (str): Unique identifier of the member (e.g., "M101").

    Returns:
        dict: A dictionary containing:
            - member_id (str): The member's unique ID
            - plan_id (str): The insurance plan associated with the member
            - status (str): Membership status (e.g., ACTIVE / INACTIVE)
            - active_from (str): Coverage start date
            - active_to (str): Coverage end date

        If the member is not found, returns:
            {"status": "NOT_FOUND"}
    """
    member = query.get_member_eligibility(member_id)

    if not member:
        return {"status": "NOT_FOUND"}

    return {
        "member_id": member.member_id,
        "plan_id": member.plan_id,
        "status": member.status,
        "active_from": str(member.active_from),
        "active_to": str(member.active_to)
    }


if __name__ == "__main__":
    print(get_member_eligibility("M101"))
    mcp.run()