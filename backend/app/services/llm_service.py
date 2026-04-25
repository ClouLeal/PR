import json
import anthropic as anthropic_sdk
from openai import OpenAI
from dataclasses import dataclass, field
from app.config import settings


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    _raw: object = field(default=None, repr=False)  # raw provider response for history building

    @property
    def is_done(self) -> bool:
        return len(self.tool_calls) == 0


def _to_openai_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


def _call_anthropic(messages: list, tools: list[dict], system: str) -> LLMResponse:
    client = anthropic_sdk.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        system=system,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "tool_use":
        calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in response.content
            if b.type == "tool_use"
        ]
        return LLMResponse(text=None, tool_calls=calls, _raw=response.content)
    return LLMResponse(text=response.content[0].text)


def _call_openrouter(messages: list, tools: list[dict], system: str) -> LLMResponse:
    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )
    all_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=settings.openrouter_model,
        tools=_to_openai_tools(tools),
        messages=all_messages,
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        calls = [
            ToolCall(id=tc.id, name=tc.function.name, input=json.loads(tc.function.arguments))
            for tc in msg.tool_calls
        ]
        return LLMResponse(text=None, tool_calls=calls, _raw=msg)
    return LLMResponse(text=msg.content)


def build_history(response: LLMResponse, results: dict[str, str]) -> list[dict]:
    """Returns the messages to append to history after tool execution.
    results = {tool_call_id: result_string}
    """
    if settings.llm_provider == "openrouter":
        assistant_msg = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.input)},
                }
                for tc in response.tool_calls
            ],
        }
        tool_msgs = [
            {"role": "tool", "tool_call_id": tc_id, "content": result}
            for tc_id, result in results.items()
        ]
        return [assistant_msg] + tool_msgs
    else:  # anthropic
        return [
            {"role": "assistant", "content": response._raw},
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": tc_id, "content": result}
                    for tc_id, result in results.items()
                ],
            },
        ]


def chat(messages: list, tools: list[dict], system: str) -> LLMResponse:
    if settings.llm_provider == "openrouter":
        return _call_openrouter(messages, tools, system)
    return _call_anthropic(messages, tools, system)
