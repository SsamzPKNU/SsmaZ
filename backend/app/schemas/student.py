from pydantic import BaseModel
from typing import Optional

class StudentBase(BaseModel):
    name: str
    parent_phone: str
    academy_id: int

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    student_id: int

    class Config:
        from_attributes = True
