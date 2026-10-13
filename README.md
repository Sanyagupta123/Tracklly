# CareerPilot

CareerPilot is a full-stack job application tracker and skill analysis dashboard for students.

## Backend

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default.

## Testing

```bash
pytest -v
```
