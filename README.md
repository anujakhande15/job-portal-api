Professional Diagrams
1. Complete Project Architecture
                                   +----------------------+
                                   |      Client/User     |
                                   |  Browser / Postman   |
                                   +----------+-----------+
                                              |
                                        HTTP Request
                                              |
                                              ▼
                               +----------------------------+
                               |        FastAPI App         |
                               |          app.py            |
                               +-------------+--------------+
                                             |
          +---------------+------------------+-------------------+
          |               |                  |                   |
          ▼               ▼                  ▼                   ▼
    Authentication    User APIs         Job APIs          Admin APIs
          |               |                  |                   |
          ▼               ▼                  ▼                   ▼
       auth.py        /register          /jobs             /admin/dashboard
                      /login             /jobs/{id}
                      /me                /jobs/search
                                         /jobs/filter
                                         /jobs/sort
                                         /jobs/pagination
                                             |
                                             ▼
                              +----------------------------+
                              |      SQLAlchemy ORM        |
                              |        models.py           |
                              +-------------+--------------+
                                            |
                                            ▼
                                 +----------------------+
                                 |      MySQL DB        |
                                 +----------------------+















JWT Authentication Flow


Register User
      │
      ▼
Password Hashing (bcrypt)
      │
      ▼
Store User in MySQL
      │
      ▼
Login
      │
      ▼
Verify Password
      │
      ▼
Generate JWT Token
      │
      ▼
Authorization Header
Bearer <token>
      │
      ▼
Protected APIs
      │
      ▼
User Data Returned








Database Diagram
                    USERS
+------------------------------------------------+
| id (PK)                                        |
| name                                           |
| email (Unique)                                 |
| password                                       |
| role                                           |
+------------------------------------------------+
                |
                |
                | 1
                |
                | N
                ▼

                    JOBS
+------------------------------------------------+
| id (PK)                                        |
| title                                          |
| company                                        |
| location                                       |
| salary                                         |
| experience                                     |
| job_type                                       |
| description                                    |
| recruiter_id (FK -> users.id)                  |
+------------------------------------------------+













API Flow
User

 │

 ▼

Register

 │

 ▼

Login

 │

 ▼

JWT Token

 │

 ▼

────────────────────────────────────────

Recruiter

 │

 ├── Create Job

 ├── Update Job

 ├── Delete Job

 └── View Own Jobs

────────────────────────────────────────

Job Seeker

 │

 ├── View Jobs

 ├── Search Jobs

 ├── Filter Jobs

 ├── Pagination

 └── Sorting

────────────────────────────────────────

Admin

 │

 └── Admin Dashboard














Folder Structure
Job_Portal_API
│
├── app.py
│      Main FastAPI Application
│
├── auth.py
│      JWT Authentication
│
├── database.py
│      Database Connection
│
├── models.py
│      SQLAlchemy Models
│
├── schemas.py
│      Pydantic Validation
│
├── requirements.txt
│
├── README.md
│
└── .env






















Features


✔ User Registration

✔ User Login

✔ JWT Authentication

✔ Password Hashing

✔ Role Based Authentication

✔ Recruiter Dashboard

✔ Admin Dashboard

✔ Create Job

✔ View Jobs

✔ View Single Job

✔ Update Job

✔ Delete Job

✔ Search Jobs

✔ Filter Jobs

✔ Pagination

✔ Sorting

✔ MySQL Integration

✔ SQLAlchemy ORM

✔ FastAPI REST APIs

✔ Environment Variables (.env)

















Technologies Used
Python

FastAPI

SQLAlchemy

MySQL

PyMySQL

JWT

Passlib (bcrypt)

Pydantic

Python-dotenv

Uvicorn










Project Workflow



User
   │
   ▼
Register
   │
   ▼
Login
   │
   ▼
JWT Token
   │
   ▼
Protected Routes
   │
   ▼
Database
   │
   ▼
Response
