from pydantic import BaseModel, EmailStr
from typing import Optional

class UserModel(BaseModel):
    image: Optional[str] = None
    username: str
    phone: int
    email: EmailStr
    password: str 
    status: bool
    role: str
