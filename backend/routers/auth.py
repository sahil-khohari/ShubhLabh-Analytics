from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets
import hashlib

from models.database import get_db
from models.schemas import User, Shop
from api_schemas import UserCreate, UserLogin, UserResponse, Token, VerifyEmailRequest, ResendOTPRequest
from utils.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.cache import get_cache, set_cache, delete_cache
from services.email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    hashed_password = get_password_hash(user.password)
    
    if db_user:
        if db_user.is_email_verified:
            raise HTTPException(status_code=400, detail="Email already registered and verified.")
        
        # Update existing unverified user
        db_user.name = user.name
        db_user.password_hash = hashed_password
        db_user.business_name = user.business_name
        db_user.business_category = user.business_category
        db_user.phone_number = user.phone_number
        db_user.store_address = user.store_address
        
        # Update their associated shop
        shop = db.query(Shop).filter(Shop.owner_id == db_user.id).first()
        if shop:
            shop.name = user.business_name or f"{user.name}'s Shop"
            shop.category = user.business_category or "Other"
            shop.location = user.store_address or "Not Provided"
            
        db.commit()
        db.refresh(db_user)
        new_user = db_user
    else:
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role="owner",
            business_name=user.business_name,
            business_category=user.business_category,
            phone_number=user.phone_number,
            store_address=user.store_address,
            is_email_verified=False
        )
        db.add(new_user)
        db.flush()

        new_shop = Shop(
            owner_id=new_user.id,
            name=user.business_name or f"{user.name}'s Shop",
            category=user.business_category or "Other",
            location=user.store_address or "Not Provided"
        )
        db.add(new_shop)
        db.commit()
        db.refresh(new_user)
    
    # Generate OTP
    otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
    
    # Store OTP in Redis
    cache_key = f"otp:{new_user.email}"
    set_cache(cache_key, {"otp": hashed_otp, "attempts": 0}, expire_seconds=300)
    
    # Send email
    email_sent = send_otp_email(new_user.email, otp)
    if not email_sent:
        # We don't delete the user because they might try again, but we should inform the frontend
        raise HTTPException(status_code=500, detail="User created, but failed to send OTP email. Please try resending the OTP.")
    
    return new_user

@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    cache_key = f"otp:{req.email}"
    otp_data = get_cache(cache_key)
    
    if not otp_data:
        raise HTTPException(status_code=400, detail="OTP expired or not found")
        
    if otp_data.get("attempts", 0) >= 3:
        delete_cache(cache_key)
        raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP.")
        
    hashed_input = hashlib.sha256(req.otp.encode()).hexdigest()
    if hashed_input != otp_data.get("otp"):
        otp_data["attempts"] = otp_data.get("attempts", 0) + 1
        set_cache(cache_key, otp_data, expire_seconds=300)
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Success
    user.is_email_verified = True
    db.commit()
    delete_cache(cache_key)
    return {"message": "Email verified successfully"}

@router.post("/resend-otp")
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")
        
    cache_key = f"otp:{req.email}"
    cooldown_key = f"otp_cooldown:{req.email}"
    
    if get_cache(cooldown_key):
        raise HTTPException(status_code=429, detail="Please wait before requesting another OTP")
        
    otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
    
    set_cache(cache_key, {"otp": hashed_otp, "attempts": 0}, expire_seconds=300)
    set_cache(cooldown_key, {"sent": True}, expire_seconds=60)
    
    email_sent = send_otp_email(user.email, otp)
    if not email_sent:
        delete_cache(cooldown_key)
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")
    
    return {"message": "OTP sent successfully"}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified. Please verify your email first."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
