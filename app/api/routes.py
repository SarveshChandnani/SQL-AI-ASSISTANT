from fastapi import APIRouter
from app.services.query_service import run_query

router = APIRouter()


@router.post("/query")
async def query_endpoint(request: dict):
    try:
        question = request.get("question")
        result = await run_query(question)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()   # 🔥 prints full error
        return {"error": str(e)}
     
     


    

    # if not question:
    #     return {"error": "Question is required"}

    # result = await run_query(question)

    # return result