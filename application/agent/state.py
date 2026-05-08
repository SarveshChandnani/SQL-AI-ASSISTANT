from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class SqlAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    question: str
    sql_query:str
    critique:str
    retry_count: int
    decision: Literal["approve", "reject"]

class GenerateQueryAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    sql_query:str

class CritiqueAgentState(TypedDict):
    question: str
    sql_query: str
    critique: str

class SqlQueryResult(BaseModel):
    query: str = Field(..., description="The SQL query that needs to be generated")

class CritiqueResult(BaseModel):
    decision: Literal["approve", "reject"]
    critique: str

    @field_validator("decision", mode="before")
    @classmethod
    def normalize_decision(cls, v):
        if isinstance(v, str):
            v = v.lower().strip()
        return v
