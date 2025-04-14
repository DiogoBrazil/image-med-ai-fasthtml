from pydantic import BaseModel 
from typing import Optional 
from uuid import UUID      

class CreateUser(BaseModel):
    full_name: str
    email: str
    password: str
    profile: str
    status: str = "active" 
    admin_id: Optional[str] = None 