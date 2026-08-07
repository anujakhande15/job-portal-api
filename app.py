

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from database import engine, SessionLocal
from models import Base, User, Job
from schemas import UserCreate, LoginUser, JobCreate

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

app = FastAPI()


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")

def home():
    return {
        "message": "Welcome to Job Portal API"
    }




@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration Successful",
        "id": new_user.id
    }




@app.post("/login")
def login(
    user: LoginUser,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }











@app.get("/me")
def my_profile(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }





@app.get("/recruiter/dashboard")
def recruiter_dashboard(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=403,
            detail="Recruiter Access Only"
        )

    return {
        "message": f"Welcome Recruiter {current_user.name}"
    }


@app.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin Access Only"
        )

    return {
        "message": "Welcome Admin",
        "admin": current_user.name
    }





@app.post("/jobs")
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=403,
            detail="Recruiters Only"
        )

    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        salary=job.salary,
        experience=job.experience,
        job_type=job.job_type,
        description=job.description,
        recruiter_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "message": "Job Created Successfully",
        "job_id": new_job.id
    }





@app.get("/jobs")
def get_jobs(
    keyword: str = None,
    location: str = None,
    job_type: str = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.company.ilike(f"%{keyword}%")
            )
        )

    if location:
        query = query.filter(
            Job.location == location
        )

    if job_type:
        query = query.filter(
            Job.job_type == job_type
        )

    jobs = query.offset(offset).limit(limit).all()

    return jobs






@app.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job Not Found"
        )

    return job



@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db_job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not db_job:
        raise HTTPException(
            status_code=404,
            detail="Job Not Found"
        )

    if db_job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )

    db_job.title = job.title
    db_job.company = job.company
    db_job.location = job.location
    db_job.salary = job.salary
    db_job.experience = job.experience
    db_job.job_type = job.job_type
    db_job.description = job.description

    db.commit()
    db.refresh(db_job)

    return {
        "message": "Job Updated Successfully"
    }





@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job Not Found"
        )

    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job Deleted Successfully"
    }




@app.get("/jobs/search")
def search_jobs(
    keyword: str,
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).filter(
        or_(
            Job.title.ilike(f"%{keyword}%"),
            Job.company.ilike(f"%{keyword}%")
        )
    ).all()

    return jobs





@app.get("/jobs/filter")
def filter_jobs(
    location: str = None,
    job_type: str = None,
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if location:
        query = query.filter(Job.location == location)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    return query.all()






@app.get("/jobs/pagination")
def pagination(
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).offset(offset).limit(limit).all()

    return jobs




@app.get("/jobs/sort")
def sort_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).order_by(
        desc(Job.salary)
    ).all()

    return jobs