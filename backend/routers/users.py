from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import schemas
import api_schemas
from models.database import get_db
from utils.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/profile", response_model=api_schemas.UserResponse)
def get_user_profile(current_user: schemas.User = Depends(get_current_user)):
    """Retrieve the profile details of the currently authenticated user."""
    return current_user

@router.put("/profile", response_model=api_schemas.UserResponse)
def update_user_profile(
    profile_update: api_schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Update the profile and business details of the currently authenticated user."""
    
    update_data = profile_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    # Sync to primary shop
    if current_user.shops and len(current_user.shops) > 0:
        primary_shop = current_user.shops[0]
        if 'business_name' in update_data:
            primary_shop.name = update_data['business_name']
        if 'business_category' in update_data:
            primary_shop.category = update_data['business_category']
        if 'store_address' in update_data:
            primary_shop.location = update_data['store_address']
        
    db.commit()
    db.refresh(current_user)
    
    return current_user
