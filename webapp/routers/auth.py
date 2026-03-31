from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1")

class LoginRequest(BaseModel):
    telegram_id: str
    phone_number: str


