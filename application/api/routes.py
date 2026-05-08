from fastapi import APIRouter,Request
from application.services.query_service import run_query



router = APIRouter()

planner_tools = None
critic_tools = None
execute_tools = None

@router.post("/query")
async def query_endpoint(request: Request, body: dict):
    try:
        question = body.get("question")
        app=request.app
        result = await run_query(
            question,
            planner_tools=app.state.planner_tools,
            critic_tools=app.state.critic_tools,
            execute_tools=app.state.execute_tools            
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
     