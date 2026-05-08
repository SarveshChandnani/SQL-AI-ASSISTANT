from langgraph.graph import StateGraph, START, END
from application.agent.state import SqlAgentState
from app.agent.nodes import agent_node
from langgraph.prebuilt import ToolNode, tools_condition
from application.agent.nodes import critic_tools_router, wrap_critic,wrap_generate,wrap_execute,critic_router
from langchain_openai import ChatOpenAI
from functools import partial


def build_graph(generate_tools, critic_tools, execute_tools, checkpointer):

    llm= ChatOpenAI(model="gpt-4o")
    graph = StateGraph(SqlAgentState)
    graph.add_node("generate_agent", wrap_generate(llm,generate_tools))
    graph.add_node("critic_agent",  wrap_critic(llm,critic_tools))
    graph.add_node("execute_agent", wrap_execute(llm,execute_tools))
    graph.add_node("generate_tools", ToolNode(generate_tools))
    graph.add_node("critic_tools", ToolNode(critic_tools))
    graph.add_node("execute_tools", ToolNode(execute_tools))


    graph.add_edge(START, "generate_agent")


    graph.add_conditional_edges(
        "generate_agent", 
        tools_condition,
        {"tools": "generate_tools", "__end__": "critic_agent"}
)
    graph.add_edge("generate_tools", "generate_agent")

  
    graph.add_conditional_edges(
    "critic_agent",
    tools_condition,
    {
        "tools": "critic_tools",
        "__end__": "__critic_router__"
    }
)

    graph.add_node("__critic_router__", lambda state: state)


    graph.add_conditional_edges("critic_tools", critic_tools_router, {
    "critic_agent": "critic_agent", "__critic_router__": "__critic_router__"
    }
)
    graph.add_conditional_edges(
    "__critic_router__",
    critic_router,
    {
        "generate_agent": "generate_agent",
        "execute_agent": "execute_agent"
    }
)

    graph.add_conditional_edges(
            "execute_agent", 
            tools_condition,
            # Map the outputs of tools_condition to your node names
            {"tools": "execute_tools", "__end__": END}
    )
    graph.add_edge("execute_tools", "execute_agent")


    return graph.compile(checkpointer=checkpointer)