from application.agent.state import SqlAgentState
from application.tools.mcp_client import get_planner_tools, get_critic_tools, get_execute_tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage,SystemMessage

def wrap_generate(generate_llm,tools):
    async def node(state):
        return await generate_query_node(state, generate_llm, tools)
    return node

def wrap_critic(critic_llm,tools):
    async def node(state):
        return await critic_node(state, critic_llm,tools)
    return node

def wrap_execute(llm,tools):
    async def node(state):
        return await execute_query_node(state, llm,tools)
    return node


def get_generate_tool_node(planner_tools):
    return ToolNode(planner_tools)

def get_critic_tool_node(critic_tools):
    return ToolNode(critic_tools)

def get_execute_tool_node(execute_tools):
    return ToolNode(execute_tools)

async def generate_query_node(state,llm,generate_query_tools):
    # System prompt for query generation
    print("generate node called")
    print("state last message:", state["messages"][-1])

    sys_prompt = SystemMessage(content="You are a SQL query generator. Create a SQL query based on the user's qustion, for schema use tools provided. Your job is to just generate the queery nothing else.")
    
    llm = llm.bind_tools(generate_query_tools)
    messages = [sys_prompt] + state["messages"]
    response = await llm.ainvoke(messages) 
    return {"messages": [response]}

async def critic_node(state,llm, critic_tools):
    print("critic node called")
    print("state last message:", state["messages"][-1])
    # System prompt for critical review
    sys_prompt = SystemMessage(content="You are a sql query critic. Review the SQL query thoroughly only by using the tools provided don't do it on your own, Only approve the read queries.")
    
    llm = llm.bind_tools(critic_tools)
    messages = [sys_prompt] + state["messages"]
    response =  await llm.ainvoke(messages) 
    return {"messages": [response]}


async def execute_query_node(state,llm, execute_tools):
    print("execute node called")
    print("state last message:", state["messages"][-1])
    # System prompt for safe execution
    sys_prompt = SystemMessage(content="You are a database executor. Safely run the validated SQL and summarize the results using the tools provided")
    
    llm = llm.bind_tools(execute_tools)
    messages = [sys_prompt] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}



def critic_router(state):
    print("critic router called")
    print("state last message:", state["messages"][-1])
    messages = state["messages"]

    # Find latest AIMessage containing tool calls
    last_ai = None

    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_ai = msg
            break

    if not last_ai:
        return "generate_agent"

    print("Found AI message:", last_ai)

    # No tool calls means fallback
    if not last_ai.tool_calls:
        return "generate_agent"

    tool_call = last_ai.tool_calls[0]

    if tool_call["name"] == "critic_evaluation":
        args = tool_call["args"]

        print("Critic evaluation args:", args)

        if (
            args["decision"] == "needs_revision"
            and state.get("retry_count", 0) < 3
        ):
            return "generate_agent"

        return "execute_agent"

    return "generate_agent"

def critic_tools_router(state):

    messages = state["messages"]

    # Find latest AIMessage
    last_ai = None

    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_ai = msg
            break

    if not last_ai or not last_ai.tool_calls:
        return "critic_agent"

    # Last requested tool
    tool_name = last_ai.tool_calls[0]["name"]

    print("Last tool requested:", tool_name)

    if tool_name == "critic_evaluation":
        return "__critic_router__"

    return "critic_agent"




 


