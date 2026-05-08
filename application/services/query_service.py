
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import aiosqlite
from application.agent.graph import  build_graph
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from application.agent.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
from application.agent.nodes import critic_node, generate_query_node, execute_query_node,get_critic_tool_node,get_generate_tool_node,get_execute_tool_node
from application.tools.mcp_client import get_planner_tools, get_critic_tools, get_execute_tools
import os
import uuid


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


async def run_query(question:str,planner_tools=None, critic_tools=None, execute_tools=None):
    print("Received question:", question)
    planner_tools = [t[1] if isinstance(t, tuple) else t for t in planner_tools]
    critic_tools = [t[1] if isinstance(t, tuple) else t for t in critic_tools]
    execute_tools = [t[1] if isinstance(t, tuple) else t for t in execute_tools]
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()
        workflow =  build_graph(planner_tools, critic_tools, execute_tools, checkpointer)
        print("Received question2:", question)
        state = {
             "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=question)
            ],
            "question": question,
            "sql_query": "",
            "critique": "",
            "retry_count": 0,
            "decision": "reject"
       }
        print("State before invoking workflow:", state)
        print("Workflow edges:", workflow)
        thread_id = str(uuid.uuid4())
        print("Generated thread_id:", thread_id)
        config = {"configurable": {"thread_id":thread_id}}
        result = await workflow.ainvoke(state, config=config)
        return {
        "answer": result["messages"][-1].content,
       }
