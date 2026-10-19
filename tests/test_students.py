from fastapi.testclient import TestClient

from app.main import create_app


def make_client(tmp_path):
    app = create_app(tmp_path / "test_students.db")
    return TestClient(app)


def student_payload(**overrides):
    return {
        "name": "Ada Lovelace",
        "date_of_birth": "2005-12-10",
        "email": "ada@example.com",
        "course": "Computer Science",
        **overrides,
    }


def test_student_crud_and_persistence(tmp_path):
    database_path = tmp_path / "students.db"
    with TestClient(create_app(database_path)) as client:
        created = client.post("/students", json=student_payload())
        assert created.status_code == 201
        student = created.json()
        student_id = student["student_id"]
        assert student["date_of_birth"] == "2005-12-10"

        assert client.get("/students").json() == [student]
        assert client.get(f"/students/{student_id}").json() == student

        updated = client.patch(
            f"/students/{student_id}", json={"course": "Mathematics"}
        )
        assert updated.status_code == 200
        assert updated.json()["course"] == "Mathematics"
        assert updated.json()["name"] == "Ada Lovelace"

    with TestClient(create_app(database_path)) as client:
        assert client.get("/students").json()[0]["student_id"] == student_id
        assert client.delete(f"/students/{student_id}").status_code == 204
        assert client.get(f"/students/{student_id}").status_code == 404


def test_filters_and_pagination(tmp_path):
    with make_client(tmp_path) as client:
        client.post("/students", json=student_payload())
        client.post(
            "/students",
            json=student_payload(
                name="Grace Hopper",
                email=None,
                phone="5551234567",
                course="Physics",
            ),
        )

        assert len(client.get("/students?name=ada").json()) == 1
        assert len(client.get("/students?course=physics").json()) == 1
        assert len(client.get("/students?limit=1").json()) == 1
        assert client.get("/students?limit=0").status_code == 422


def test_validation_and_missing_records(tmp_path):
    with make_client(tmp_path) as client:
        assert client.post(
            "/students",
            json=student_payload(email=None),
        ).status_code == 422
        assert client.post(
            "/students",
            json=student_payload(date_of_birth="not-a-date"),
        ).status_code == 422
        assert client.post(
            "/students",
            json=student_payload(name="   "),
        ).status_code == 422
        assert client.post(
            "/students",
            json=student_payload(email="not-an-email"),
        ).status_code == 422
        assert client.get("/students/999").status_code == 404
        assert client.patch("/students/999", json={"course": "Physics"}).status_code == 404
        assert client.delete("/students/999").status_code == 404


def test_update_cannot_remove_all_contact_information(tmp_path):
    with make_client(tmp_path) as client:
        student_id = client.post("/students", json=student_payload()).json()[
            "student_id"
        ]
        response = client.patch(
            f"/students/{student_id}", json={"email": None}
        )
        assert response.status_code == 422
        assert client.get(f"/students/{student_id}").json()["email"] == "ada@example.com"
