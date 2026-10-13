# CareerPilot architecture

CareerPilot is a lightweight full-stack job tracking app built around a FastAPI backend and a React + Vite frontend.

## Backend

- FastAPI exposes CRUD endpoints for applications and a skill-analysis endpoint.
- SQLite stores application records in a persistent `careerpilot.db` database in the project root.
- The database path is customizable via `CAREERPILOT_DB_PATH`, which helps tests run against isolated temporary databases.
- Application validation is handled by Pydantic schemas with enforced status values and sanitization for blank inputs.
- Rule-based skill detection is implemented in `app/analyzer.py` using a dictionary of technical terms and aliases.

## Frontend

- The React dashboard displays application counts, saved job records, and skill-analysis output.
- API calls happen through a shared `src/api.js` module so request logic is reusable and consistent.
- Vite uses a configurable `VITE_API_BASE_URL` environment variable for backend connection settings.
- The UI includes create, edit, delete, and analysis flows with clear validation and error states.

## Current MVP scope

- Application tracking with persistent storage
- Status-based filtering in the dashboard statistics
- Rule-based technical skill detection for job descriptions
- Local development using Python + FastAPI and React + Vite

## Future enhancements

- Authentication and user-specific records
- Better NLP-powered skill extraction
- Application notes and interview follow-up tracking
