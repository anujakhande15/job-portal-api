from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# ==========================
# User Model
# ==========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="job_seeker")


# ==========================
# Job Model
# ==========================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    location = Column(String(100), nullable=False)
    salary = Column(Integer)
    experience = Column(String(50))
    job_type = Column(String(50))
    description = Column(Text)

    recruiter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    recruiter = relationship(
        "User",
        backref="jobs"
    )