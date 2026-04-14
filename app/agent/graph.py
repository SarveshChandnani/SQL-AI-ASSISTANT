from langgraph.graph import StateGraph, START, END
from app.agent.state import SqlAgentState
from app.agent.nodes import agent_node
from langgraph.prebuilt import ToolNode, tools_condition
from functools import partial

def build_graph(tools,llm_with_tools,checkpointer=None):
    print("Building graph with tools:", tools)
    tool_node = ToolNode(tools = list(tools))
    graph = StateGraph(SqlAgentState)

    graph.add_node('agent_node',partial(agent_node, llm_with_tools=llm_with_tools))
    graph.add_node('tools', tool_node)

    graph.add_edge(START, 'agent_node')
    graph.add_conditional_edges("agent_node", tools_condition)
    graph.add_edge('tools', 'agent_node')
    return graph.compile(checkpointer=checkpointer)