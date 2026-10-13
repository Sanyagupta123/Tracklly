from contextlib import asynccontextmanager, closing
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import analyze_job_description
from app.database import get_connection, initialize_database
from app.schemas import AnalysisRequest, ApplicationCreate, ApplicationUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="CareerPilot API",
    description="Job Application Tracking and Skill Analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CareerPilot API is running."}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "CareerPilot"}


def row_to_dict(row: Any) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def fetch_application(application_id: int) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT id, company, role, job_description, status, created_at FROM applications WHERE id = ?",
            (application_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@app.post("/applications", status_code=201)
def create_application(payload: ApplicationCreate) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO applications (company, role, job_description, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.company,
                payload.role,
                payload.job_description,
                payload.status,
            ),
        )
        connection.commit()
        application_id = cursor.lastrowid
        row = connection.execute(
            "SELECT id, company, role, job_description, status, created_at FROM applications WHERE id = ?",
            (application_id,),
        ).fetchone()
    return row_to_dict(row)


@app.get("/applications")
def list_applications() -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT id, company, role, job_description, status, created_at FROM applications ORDER BY id DESC"
        ).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/applications/{application_id}")
def get_application(application_id: int) -> dict[str, Any]:
    return fetch_application(application_id)


@app.patch("/applications/{application_id}")
def update_application(application_id: int, payload: ApplicationUpdate) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            UPDATE applications
            SET company = ?, role = ?, job_description = ?, status = ?
            WHERE id = ?
            """,
            (
                payload.company,
                payload.role,
                payload.job_description,
                payload.status,
                application_id,
            ),
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Application not found")
        row = connection.execute(
            "SELECT id, company, role, job_description, status, created_at FROM applications WHERE id = ?",
            (application_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@app.delete("/applications/{application_id}")
def delete_application(application_id: int) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        cursor = connection.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted successfully", "id": application_id}


@app.post("/analyze")
def analyze_text(payload: AnalysisRequest) -> dict[str, Any]:
    return analyze_job_description(payload.text)
