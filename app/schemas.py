from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ApplicationStatus = Literal["Wishlist", "Applied", "Interview", "Offer", "Rejected"]


class ApplicationBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(default="", max_length=20000)
    status: ApplicationStatus = "Applied"

    @field_validator("company", "role")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None:
            raise ValueError("must not be blank")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value: str) -> str:
        if value is None:
            return ""
        return value.strip()


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    company: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., max_length=20000)
    status: ApplicationStatus


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(default="", max_length=20000)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        if value is None:
            return ""
        return value.strip()
