from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import services.ai_service as ai_service
from utils.auth import get_current_user, get_current_shop
from models.database import get_db
import models.schemas as schemas

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    dependencies=[Depends(get_current_user)]
)

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask-business-question")
def ask_business_question(
    payload: QuestionRequest, 
    shop: schemas.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """
    Accepts a natural language business question, runs it through the LangChain 
    Text-to-SQL pipeline using an isolated temporary dataset, and returns the answer.
    """
    result = ai_service.ask_database(payload.question, shop.id, db)
    return result
