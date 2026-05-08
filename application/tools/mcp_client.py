from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
import sys
import os


# async def get_tools():
#     # SERVERS = {
#     #     "math": {
#     #         "transport": "stdio",
#     #         "command": "C:/Python311/Scripts/uv.exe",
#     #         "args": [
#     #             "run",
#     #             "D:/gen-ai/LanGraph/sql-query-agent/sql-query-agent/mcp-server/main.py"
#     #         ]
#     #     }
#     # }

#     SERVERS = {
#         "math": {
#             "transport": "stdio",
#             "command": sys.executable,  
#             "args": [
#                 "-u",  
#                 os.path.abspath(
#                     "D:/gen-ai/LanGraph/SQL-AI-Assiatant/mcp-server/main.py"
#                 )
#             ]
#         }
#     }

#     client = MultiServerMCPClient(SERVERS)
#     tools = await client.get_tools()
#     # tools = [t[1] if isinstance(t, tuple) else t for t in tools]
#     return tools

async def get_planner_tools():
    SERVERS = {
        "math": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                "-u",    
                os.path.abspath(
                    "D:/gen-ai/LanGraph/SQL-AI-Assiatant/mcp-server/planner_node_tools.py"
                )
            ]
        }
    }
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    return tools

@tool
def critic_evaluation(decision: str, feedback: str):
    """Finalize critique. Decision must be 'approved' or 'needs_revision'."""
    pass


async def get_critic_tools():
    SERVERS = {
        "math": {
            "transport": "stdio",
           "command": sys.executable,
            "args": [
                "-u",  
                os.path.abspath(
                    "D:/gen-ai/LanGraph/SQL-AI-Assiatant/mcp-server/critic_node_tools.py"
                )
            ]
        }
    }
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    combined_tools = tools + [critic_evaluation]
    return combined_tools

async def get_execute_tools():
    SERVERS = {
        "math": {
            "transport": "stdio",
             "command": sys.executable,
            "args": [
                "-u",   
                os.path.abspath(
                    "D:/gen-ai/LanGraph/SQL-AI-Assiatant/mcp-server/execute_node_tools.py"
                )
            ]
        }
    }
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    return tools

