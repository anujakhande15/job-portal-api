from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, SessionLocal
from models import Base, User, Job, Application, SavedJob
from schemas import (
    UserCreate,
    LoginUser,
    JobCreate,
    ApplicationCreate
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


app = FastAPI(
    title="Job Portal API",
    description="A REST API for job seekers, recruiters and administrators",
    version="1.0.0"
)


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

    
    if user.role not in ["job_seeker", "recruiter"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    
    email = form_data.username
    password = form_data.password

    
    db_user = db.query(User).filter(
        User.email == email
    ).first()

    
    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    
    if not verify_password(
        password,
        db_user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    
    token = create_access_token({
        "sub": db_user.email,
        "role": db_user.role
    })

    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin Access Only"
        )

    total_users = db.query(User).count()

    total_recruiters = db.query(User).filter(
        User.role == "recruiter"
    ).count()

    total_job_seekers = db.query(User).filter(
        User.role == "job_seeker"
    ).count()

    total_jobs = db.query(Job).count()

    total_applications = db.query(
        Application
    ).count()

    total_saved_jobs = db.query(
        SavedJob
    ).count()

    return {
        "total_users": total_users,
        "total_recruiters": total_recruiters,
        "total_job_seekers": total_job_seekers,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_saved_jobs": total_saved_jobs
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
    keyword: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if keyword:

        query = query.filter(
            or_(
                Job.title.ilike(
                    f"%{keyword}%"
                ),
                Job.company.ilike(
                    f"%{keyword}%"
                )
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

    jobs = query.offset(
        offset
    ).limit(
        limit
    ).all()

    return jobs


@app.get("/jobs/search")
def search_jobs(
    keyword: str,
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).filter(
        or_(
            Job.title.ilike(
                f"%{keyword}%"
            ),
            Job.company.ilike(
                f"%{keyword}%"
            )
        )
    ).all()

    return jobs


@app.get("/jobs/filter")
def filter_jobs(
    location: str | None = None,
    job_type: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(Job)

    if location:

        query = query.filter(
            Job.location == location
        )

    if job_type:

        query = query.filter(
            Job.job_type == job_type
        )

    return query.all()


@app.get("/jobs/pagination")
def pagination(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).offset(
        offset
    ).limit(
        limit
    ).all()

    return jobs


@app.get("/jobs/sort")
def sort_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).order_by(
        desc(Job.salary)
    ).all()

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

    if current_user.role != "recruiter":

        raise HTTPException(
            status_code=403,
            detail="Recruiters Only"
        )

    if db_job.recruiter_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You can only update your own jobs"
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

    if current_user.role != "recruiter":

        raise HTTPException(
            status_code=403,
            detail="Recruiters Only"
        )

    if job.recruiter_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="You can only delete your own jobs"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job Deleted Successfully"
    }


@app.post("/jobs/{job_id}/apply")
def apply_job(
    job_id: int,
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "job_seeker":

        raise HTTPException(
            status_code=403,
            detail="Only Job Seekers Can Apply"
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job Not Found"
        )

    existing_application = db.query(
        Application
    ).filter(
        Application.job_id == job_id,
        Application.user_id == current_user.id
    ).first()

    if existing_application:

        raise HTTPException(
            status_code=400,
            detail="Already Applied For This Job"
        )

    new_application = Application(
        job_id=job_id,
        user_id=current_user.id,
        resume=application.resume,
        status="Applied"
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return {
        "message": "Application Submitted Successfully",
        "application_id": new_application.id
    }


@app.get("/my-applications")
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    applications = db.query(
        Application
    ).filter(
        Application.user_id == current_user.id
    ).all()

    return applications


@app.get("/recruiter/applications")
def recruiter_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":

        raise HTTPException(
            status_code=403,
            detail="Recruiters Only"
        )

    applications = (
        db.query(Application)
        .join(Job)
        .filter(
            Job.recruiter_id == current_user.id
        )
        .all()
    )

    return applications


@app.post("/jobs/{job_id}/save")
def save_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "job_seeker":

        raise HTTPException(
            status_code=403,
            detail="Only Job Seekers Can Save Jobs"
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job Not Found"
        )

    existing = db.query(
        SavedJob
    ).filter(
        SavedJob.job_id == job_id,
        SavedJob.user_id == current_user.id
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Job Already Saved"
        )

    saved_job = SavedJob(
        job_id=job_id,
        user_id=current_user.id
    )

    db.add(saved_job)
    db.commit()

    return {
        "message": "Job Saved Successfully"
    }


@app.get("/saved-jobs")
def saved_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    saved = db.query(
        SavedJob
    ).filter(
        SavedJob.user_id == current_user.id
    ).all()

    return saved


@app.delete("/saved-jobs/{job_id}")
def remove_saved_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    saved = db.query(
        SavedJob
    ).filter(
        SavedJob.job_id == job_id,
        SavedJob.user_id == current_user.id
    ).first()

    if not saved:
        raise HTTPException(
            status_code=404,
            detail="Saved Job Not Found"
        )

    db.delete(saved)
    db.commit()

    return {
        "message": "Job Removed From Saved Jobs"
    }