from fastapi import APIRouter, Depends
from pydantic import BaseModel
import services.ai_service as ai_service
from utils.auth import get_current_user

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    dependencies=[Depends(get_current_user)]
)

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask-business-question")
def ask_business_question(payload: QuestionRequest):
    """
    Accepts a natural language business question, runs it through the LangChain 
    Text-to-SQL pipeline, and returns the generated explanation and SQL.
    """
    result = ai_service.ask_database(payload.question)
    return result
