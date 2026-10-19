from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class StudentFields(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: str | None = Field(default=None, max_length=254, pattern=EMAIL_PATTERN)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None

    @model_validator(mode="after")
    def require_contact_information(self):
        if not self.email and not self.phone:
            raise ValueError("At least one of email or phone is required")
        return self


class StudentCreate(StudentFields):
    pass


class StudentUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    email: str | None = Field(default=None, max_length=254, pattern=EMAIL_PATTERN)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None

    @model_validator(mode="after")
    def require_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Student(StudentFields):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
