from fastapi import HTTPException, FastAPI
from starlette import status
from schema import Request
from dotenv import load_dotenv
from services import chat

load_dotenv()

app = FastAPI()

@app.post(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    summary="Researches about the company in the internet"
)
async def process_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
):
    try:
        result = await chat.run_query(request.text,userId,realmId,leadId)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

