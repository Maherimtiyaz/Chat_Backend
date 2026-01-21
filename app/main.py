from fastapi import FastAPI
from app.api import auth, chat
from app.core.security import get_current_user
from fastapi import Depends

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)

# Test route
@app.get("/")
async def root():
    return {"message": "Real-time chat backend is starting!"}

# Protected route example
@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"user": user}