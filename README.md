 backend/
 ├── app/
 │   ├── api/                   -- FastAPI route handlers
 │   │   ├── user_routes.py
 │   │   ├── document_routes.py
 │   │   └── ingestion_routes.py
 │   ├── core/                  -- Configs, auth, utils
 │   │   ├── config.py
 │   │   ├── auth.py
 │   │   └── security.py
 │   ├── db/                    -- MongoDB init, connection, schemas
 │   │   ├── mongodb.py
 │   │   └── models.py
 │   ├── models/                -- Pydantic models
 │   │   ├── user.py
 │   │   ├── document.py
 │   │   └── ingestion.py
 │   ├── services/              --  Business logic
 │   │   ├── user_service.py
 │   │   ├── document_service.py
 │   │   └── ingestion_service.py
 │   ├── ingestion/             -- Ingestion logic (microservice)
 │   │   └── worker.py
 │   ├── tests/                 -- Unit tests
 │   │   ├── constants.py
 │   │   ├── test_user.py
 │   │   ├── test_document.py
 │   │   └── test_ingestion.py
 │   └── main.py                -- FastAPI app entrypoint
 ├── docker-compose.yml
 ├── Dockerfile
 └── README.md


 # Document Management & Ingestion System

## Overview
This application provides user, document, and ingestion management with JWT-based authentication and role-based access control using FastAPI and MongoDB.

## Features
- User registration and login
- Role-based access (Admin, Editor, Viewer)
- CRUD operations for documents
- Ingestion pipeline trigger and tracking
- JWT Auth, error handling, unit tests
- Dockerized deployment

## Tech Stack
- Backend: Python, FastAPI
- Database: MongoDB
- Auth: JWT
- Container: Docker & Docker Compose
- Testing: Pytest

## Running Locally with Docker
```bash
git clone <repo_url>
cd backend
docker-compose up --build
```
Access the API at: `http://localhost:8000/api/v1/docs`

## Running Tests
```bash
docker-compose exec backend pytest
```

## Manual Local Setup (without Docker)

1. **Install dependencies:**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```
2. *** Configure Env variables ***
```bash
MONGODB_URI="mongodb://localhost:27017/your_database_name"
SECRET_KEY="your_jwt_secret_key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
3. *** Start mongodb on local ***
```bash
mongod
```
4. *** Run FastAPI application ***
```bash 
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
5. *** Access the API docs ***
```bash 
http://localhost:8000/api/v1/docs
```

6. *** Run Tests ***
```bash 
PYTHONPATH=./app pytest
```



## Deployment
Can be deployed to any cloud with Docker/Kubernetes support.


