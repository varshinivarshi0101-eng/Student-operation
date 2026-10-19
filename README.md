# Students Database API

A Python backend for managing student records with FastAPI and SQLite. The API
supports creating, listing, filtering, retrieving, updating, and deleting
students. The optional Ollama extension from the assignment is not included.

## Requirements

- Python 3.10 or newer
- pip

## Install and run

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. Interactive API documentation
is at <http://127.0.0.1:8000/docs>. On first startup, SQLite creates
`data/students.db` automatically.

To store the database elsewhere, set `STUDENT_DATABASE_PATH` before starting
the server:

```powershell
$env:STUDENT_DATABASE_PATH = "C:\path\to\students.db"
uvicorn app.main:app --reload
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/students` | Create a student |
| `GET` | `/students` | List students; optional `name`, `course`, `limit`, and `offset` query parameters |
| `GET` | `/students/{student_id}` | Retrieve one student |
| `PATCH` | `/students/{student_id}` | Update one or more student fields |
| `DELETE` | `/students/{student_id}` | Delete a student |

Each student has an auto-generated unique ID, name, date of birth, and at least
one contact method (`email` or `phone`). Course, address, and enrollment date
are optional. Dates use the `YYYY-MM-DD` format. Listing is limited to 100
records per request.

### Example requests

Create a student:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/students `
  -ContentType "application/json" `
  -Body '{"name":"Ada Lovelace","date_of_birth":"2005-12-10","email":"ada@example.com","course":"Computer Science"}'
```

List or filter students:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/students?course=computer"
```

Update a student's course:

```powershell
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/students/1 `
  -ContentType "application/json" -Body '{"course":"Mathematics"}'
```

## Tests

```powershell
python -m pytest
```

Tests use a temporary SQLite database and do not modify the application database.
