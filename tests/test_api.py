import pytest
from fastapi.testclient import TestClient

from app.database import initialize_database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "careerpilot-test.db"
    monkeypatch.setenv("CAREERPILOT_DB_PATH", str(database_path))
    initialize_database(database_path)
    with TestClient(app) as test_client:
        yield test_client


def test_root_returns_success(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_returns_success(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_application_success(client):
    payload = {
        "company": "Acme",
        "role": "Python Developer",
        "job_description": "Build Python and FastAPI services.",
        "status": "Applied",
    }
    response = client.post("/applications", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert "created_at" in body
    assert body["company"] == "Acme"
    assert body["status"] == "Applied"


def test_create_application_defaults(client):
    response = client.post("/applications", json={"company": "Example", "role": "Engineer"})
    assert response.status_code == 201
    body = response.json()
    assert body["job_description"] == ""
    assert body["status"] == "Applied"


def test_invalid_status_rejected(client):
    response = client.post("/applications", json={"company": "A", "role": "B", "status": "Unknown"})
    assert response.status_code == 422


def test_missing_company_or_role_rejected(client):
    assert client.post("/applications", json={"role": "Engineer"}).status_code == 422
    assert client.post("/applications", json={"company": "Acme"}).status_code == 422


def test_blank_company_or_role_rejected(client):
    assert client.post("/applications", json={"company": "   ", "role": "Engineer"}).status_code == 422
    assert client.post("/applications", json={"company": "Acme", "role": "   "}).status_code == 422


def test_oversized_inputs_rejected(client):
    oversized_company = "x" * 101
    oversized_role = "y" * 101
    oversized_description = "z" * 20001
    assert client.post("/applications", json={"company": oversized_company, "role": "Engineer"}).status_code == 422
    assert client.post("/applications", json={"company": "Acme", "role": oversized_role}).status_code == 422
    assert client.post("/applications", json={"company": "Acme", "role": "Engineer", "job_description": oversized_description}).status_code == 422


def test_list_applications_returns_records(client):
    client.post("/applications", json={"company": "A", "role": "R"})
    client.post("/applications", json={"company": "B", "role": "Q"})
    response = client.get("/applications")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["company"] == "B"


def test_empty_database_returns_empty_list(client):
    response = client.get("/applications")
    assert response.status_code == 200
    assert response.json() == []


def test_known_id_returns_correct_record(client):
    created = client.post("/applications", json={"company": "Acme", "role": "Engineer"}).json()
    response = client.get(f"/applications/{created['id']}")
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"


def test_unknown_id_returns_404(client):
    response = client.get("/applications/999")
    assert response.status_code == 404


def test_valid_update_changes_record(client):
    created = client.post("/applications", json={"company": "Acme", "role": "Engineer"}).json()
    response = client.patch(
        f"/applications/{created['id']}",
        json={"company": "NewCo", "role": "Senior Engineer", "job_description": "Need AWS and Python.", "status": "Interview"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["company"] == "NewCo"
    assert body["status"] == "Interview"


def test_invalid_update_status_rejected(client):
    created = client.post("/applications", json={"company": "Acme", "role": "Engineer"}).json()
    response = client.patch(
        f"/applications/{created['id']}",
        json={"company": "Acme", "role": "Engineer", "job_description": "", "status": "Unknown"},
    )
    assert response.status_code == 422


def test_update_unknown_id_returns_404(client):
    response = client.patch(
        "/applications/999",
        json={"company": "Acme", "role": "Engineer", "job_description": "", "status": "Applied"},
    )
    assert response.status_code == 404


def test_valid_deletion_removes_record(client):
    created = client.post("/applications", json={"company": "Acme", "role": "Engineer"}).json()
    response = client.delete(f"/applications/{created['id']}")
    assert response.status_code == 200
    assert client.get(f"/applications/{created['id']}").status_code == 404


def test_delete_unknown_id_returns_404(client):
    response = client.delete("/applications/999")
    assert response.status_code == 404


def test_python_skill_detected(client):
    response = client.post("/analyze", json={"text": "We need a Python developer with FastAPI skills and Docker experience."})
    assert response.status_code == 200
    data = response.json()
    assert "Python" in data["detected_skills"]
    assert "FastAPI" in data["detected_skills"]
    assert data["skill_count"] >= 3


def test_multiple_skills_detected(client):
    response = client.post("/analyze", json={"text": "Work with React, AWS, SQL, and Docker in a Python environment."})
    assert response.status_code == 200
    skills = response.json()["detected_skills"]
    for skill in ["Python", "React", "AWS", "SQL", "Docker"]:
        assert skill in skills


def test_case_insensitive_matching(client):
    response = client.post("/analyze", json={"text": "experience with python, react.js, and GIT."})
    assert response.status_code == 200
    skills = response.json()["detected_skills"]
    assert "Python" in skills
    assert "React" in skills
    assert "Git" in skills


def test_aliases_work(client):
    response = client.post("/analyze", json={"text": "Need scikit-learn, machine learning, and postgres experience."})
    assert response.status_code == 200
    skills = response.json()["detected_skills"]
    assert "Scikit-learn" in skills
    assert "Machine Learning" in skills
    assert "PostgreSQL" in skills


def test_duplicate_aliases_do_not_create_duplicates(client):
    response = client.post("/analyze", json={"text": "Python and python and fastapi REST API using FastAPI."})
    assert response.status_code == 200
    data = response.json()
    assert data["skill_count"] == len(set(data["detected_skills"]))
    assert "Python" in data["detected_skills"]
    assert "FastAPI" in data["detected_skills"]
    assert "REST APIs" in data["detected_skills"]


def test_unrelated_words_do_not_match(client):
    response = client.post("/analyze", json={"text": "The project is about a pythonic approach, not a literal Python job requirement. The pupils discussed gitlike ideas and dockerized stories."})
    assert response.status_code == 200
    skills = response.json()["detected_skills"]
    assert "Python" not in skills
    assert "Git" not in skills
    assert "Docker" not in skills


def test_empty_description_handled(client):
    response = client.post("/analyze", json={"text": "   "})
    assert response.status_code == 200
    assert response.json() == {"detected_skills": [], "skill_count": 0}


def test_records_persist_across_connections(client):
    created = client.post("/applications", json={"company": "PersistCo", "role": "Engineer"}).json()
    response = client.get(f"/applications/{created['id']}")
    assert response.status_code == 200
    assert response.json()["company"] == "PersistCo"


def test_database_path_is_configurable(monkeypatch, tmp_path):
    custom_path = tmp_path / "custom.db"
    monkeypatch.setenv("CAREERPILOT_DB_PATH", str(custom_path))
    initialize_database(custom_path)
    assert custom_path.exists()

    with TestClient(app) as test_client:
        response = test_client.get("/applications")
        assert response.status_code == 200
        assert response.json() == []
