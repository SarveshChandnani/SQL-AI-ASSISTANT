from app.agent.state import SqlAgentState

async def agent_node(state: SqlAgentState, llm_with_tools):
    print("Agent node received state:", state)
    messages = state["messages"]
    response =await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}
