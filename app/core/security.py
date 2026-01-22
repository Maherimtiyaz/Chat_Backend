from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "super-secret-key-change-later"
ALGORITHM = "HS256"


# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

# Verify Password
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# Create Access Token
def create_access_token(data: dict, expires_minutes: int=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# Verify Token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") # Return username
    except JWTError:
        return None