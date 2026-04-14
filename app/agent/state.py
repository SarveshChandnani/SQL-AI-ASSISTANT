from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SqlAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    retry_count: int
    last_error: str
    last_query: str