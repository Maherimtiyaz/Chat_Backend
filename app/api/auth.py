from fastapi import APIRouter, HTTPException
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# TEMP fake DB (replce with real DB later)
fake_users_db = {}

# Register User

@router.post("/signup")
async def signup(username: str, password: str):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    fake_users_db[username] = hash_password(password)
    return {"message": "user registered successfully!"}

# Login User

@router.post("/login")
async def login(username: str, password: str):
    hashed = fake_users_db.get(username)
    if not hashed or not verify_password(password, hashed):
        raise HTTPException(status_code=401, detail="Inavlid Credentials")
    
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}