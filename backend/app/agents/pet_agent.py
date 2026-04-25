from sqlalchemy.orm import Session
from app.services.llm_service import chat, build_history
from app.agents.tools.search_records import search_records, SEARCH_RECORDS_TOOL
from app.agents.tools.health_summary import health_summary, HEALTH_SUMMARY_TOOL

SYSTEM_PROMPT = (
    "You are a veterinary health assistant. "
    "You already have access to the pet's data — never ask the user for a pet ID. "
    "Always call a tool to look up information before answering. "
    "Answer ONLY based on what the tools return. "
    "If no relevant information is found, say so clearly. "
    "Never invent or assume information not present in the documents."
)

TOOLS = [SEARCH_RECORDS_TOOL, HEALTH_SUMMARY_TOOL]


def execute_tool(name: str, inputs: dict, pet_id: str, db: Session) -> str:
    if name == "search_records":
        return search_records(inputs["query"], pet_id)
    if name == "health_summary":
        return health_summary(pet_id, db)
    return "Tool not found."


def run_agent(message: str, pet_id: str, db: Session) -> str:
    messages = [{"role": "user", "content": message}]

    while True:
        response = chat(messages, TOOLS, SYSTEM_PROMPT)

        if response.is_done:
            return response.text

        results = {
            tc.id: execute_tool(tc.name, tc.input, pet_id, db)
            for tc in response.tool_calls
        }

        messages.extend(build_history(response, results))
