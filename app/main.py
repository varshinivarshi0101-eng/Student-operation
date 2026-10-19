import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, Response, status

from database import StudentDatabase
from schemas import Student, StudentCreate, StudentUpdate


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "students.db"


def create_app(database_path: str | Path | None = None) -> FastAPI:
    db = StudentDatabase(
        database_path or os.getenv("STUDENT_DATABASE_PATH", str(DEFAULT_DATABASE_PATH))
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        db.initialize()
        yield

    app = FastAPI(
        title="Students Database API",
        description="A student records CRUD API backed by SQLite.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.student_database = db

    @app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
    def create_student(student: StudentCreate, request: Request):
        database: StudentDatabase = request.app.state.student_database
        values = student.model_dump(mode="json")
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        with database.connect() as connection:
            cursor = connection.execute(
                f"INSERT INTO students ({columns}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            row = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return dict(row)

    @app.get("/students", response_model=list[Student])
    def list_students(
        request: Request,
        name: Annotated[str | None, Query(max_length=100)] = None,
        course: Annotated[str | None, Query(max_length=100)] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        database: StudentDatabase = request.app.state.student_database
        conditions = []
        parameters: list[object] = []
        if name:
            conditions.append("name LIKE ? COLLATE NOCASE")
            parameters.append(f"%{name}%")
        if course:
            conditions.append("course LIKE ? COLLATE NOCASE")
            parameters.append(f"%{course}%")
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        parameters.extend((limit, offset))
        with database.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM students {where_clause} "
                "ORDER BY student_id LIMIT ? OFFSET ?",
                parameters,
            ).fetchall()
        return [dict(row) for row in rows]

    @app.get("/students/{student_id}", response_model=Student)
    def get_student(student_id: int, request: Request):
        database: StudentDatabase = request.app.state.student_database
        with database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)

    @app.patch("/students/{student_id}", response_model=Student)
    def update_student(student_id: int, student: StudentUpdate, request: Request):
        database: StudentDatabase = request.app.state.student_database
        updates = student.model_dump(exclude_unset=True, mode="json")
        if "name" in updates and updates["name"] is None:
            raise HTTPException(status_code=422, detail="name cannot be null")
        if "date_of_birth" in updates and updates["date_of_birth"] is None:
            raise HTTPException(
                status_code=422, detail="date_of_birth cannot be null"
            )
        with database.connect() as connection:
            existing = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
            if existing is None:
                raise HTTPException(status_code=404, detail="Student not found")
            merged_email = updates.get("email", existing["email"])
            merged_phone = updates.get("phone", existing["phone"])
            if not merged_email and not merged_phone:
                raise HTTPException(
                    status_code=422,
                    detail="At least one of email or phone must be provided",
                )
            assignments = ", ".join(f"{column} = ?" for column in updates)
            if updates:
                connection.execute(
                    f"UPDATE students SET {assignments} WHERE student_id = ?",
                    (*updates.values(), student_id),
                )
            row = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
        return dict(row)

    @app.delete(
        "/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT
    )
    def delete_student(student_id: int, request: Request):
        database: StudentDatabase = request.app.state.student_database
        with database.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE student_id = ?", (student_id,)
            )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
