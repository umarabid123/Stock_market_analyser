from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import USERS
from app.core.security import create_access_token

router = APIRouter()


class RegisterPayload(BaseModel):
    username: str
    password: str


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(payload: RegisterPayload):
    if payload.username in USERS:
        raise HTTPException(status_code=400, detail="User exists")
    USERS[payload.username] = {"username": payload.username, "password": payload.password}
    token = create_access_token(payload.username)
    return {"access_token": token}


@router.post("/login")
def login(payload: LoginPayload):
    user = USERS.get(payload.username)
    if not user or user.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(payload.username)
    return {"access_token": token}
