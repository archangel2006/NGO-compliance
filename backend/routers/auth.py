from fastapi import APIRouter
from pydantic import BaseModel
from backend.auth import login

router = APIRouter()

class LoginRequest(BaseModel):
    email:    str
    password: str

@router.post("/login")
def login_endpoint(body: LoginRequest):
    return login(body.email, body.password)