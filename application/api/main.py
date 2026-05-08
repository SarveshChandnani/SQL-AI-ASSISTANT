from fastapi import FastAPI
from application.api.routes import router
from application.tools.mcp_client import get_planner_tools, get_critic_tools, get_execute_tools

app = FastAPI(title="SQL AI Assistant")

@app.on_event("startup")
async def startup():
    app.state.planner_tools = await get_planner_tools()
    app.state.critic_tools = await get_critic_tools()
    app.state.execute_tools = await get_execute_tools()
app.include_router(router)