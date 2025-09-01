from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    contact: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    vitals: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: int

    class Config:
        orm_mode = True
