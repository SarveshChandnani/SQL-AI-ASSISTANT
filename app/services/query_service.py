from langchain_openai import ChatOpenAI
from app.tools.mcp_client import get_tools
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import aiosqlite
from app.agent.graph import  build_graph
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from app.agent.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def run_query(query:str):
    print("Received query:", query)
    llm = ChatOpenAI(model="gpt-4o")

    tools = await get_tools()
    tools = [t[1] if isinstance(t, tuple) else t for t in tools]
    print("Retrieved tools:", tools)
    llm_with_tools = llm.bind_tools(tools)

    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()
        workflow = build_graph(tools,llm_with_tools,checkpointer)
        state = {
            "messages": [
                SystemMessage(content= SYSTEM_PROMPT),
                HumanMessage(content=query)
                ]
        }
        config = {"configurable": {"thread_id": "thread_2"}}
        result = await workflow.ainvoke(state, config=config)
        return {
        "answer": result["messages"][-1].content,
       }
