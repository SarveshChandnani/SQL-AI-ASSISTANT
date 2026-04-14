from langchain_mcp_adapters.client import MultiServerMCPClient
import sys
import os
async def get_tools():
    # SERVERS = {
    #     "math": {
    #         "transport": "stdio",
    #         "command": "C:/Python311/Scripts/uv.exe",
    #         "args": [
    #             "run",
    #             "D:/gen-ai/LanGraph/sql-query-agent/sql-query-agent/mcp-server/main.py"
    #         ]
    #     }
    # }

    SERVERS = {
        "math": {
            "transport": "stdio",
            "command": sys.executable,  
            "args": [
                "-u",  
                os.path.abspath(
                    "D:/gen-ai/LanGraph/SQL-AI-Assiatant/mcp-server/main.py"
                )
            ]
        }
    }

    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    # tools = [t[1] if isinstance(t, tuple) else t for t in tools]
    return tools