from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "job_seeker"


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: int | None = None
    experience: str | None = None
    job_type: str | None = None
    description: str | None = None


class ApplicationCreate(BaseModel):
    resume: str