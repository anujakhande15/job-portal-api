from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="job_seeker", nullable=False)

    jobs = relationship("Job", back_populates="recruiter")
    applications = relationship("Application", back_populates="user")
    saved_jobs = relationship("SavedJob", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    location = Column(String(100), nullable=False)
    salary = Column(Integer, nullable=True)
    experience = Column(String(50), nullable=True)
    job_type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    recruiter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    saved_jobs = relationship("SavedJob", back_populates="job")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    resume = Column(String(255), nullable=True)
    status = Column(String(50), default="Applied", nullable=False)

    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "user_id",
            name="unique_job_application"
        ),
    )


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    job = relationship("Job", back_populates="saved_jobs")
    user = relationship("User", back_populates="saved_jobs")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "job_id",
            name="unique_saved_job"
        ),
    )