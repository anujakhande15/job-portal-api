from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: int
    experience: str
    job_type: str
    description: str