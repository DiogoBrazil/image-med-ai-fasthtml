from pydantic import BaseModel, EmailStr
from typing import Optional 

class UpdateUser(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    profile: Optional[str] = None
    status: Optional[str] = None
    admin_id: Optional[str] = None