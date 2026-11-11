from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class BriefBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=180, description="Name of the company")
    industry: str = Field(default="Paint / Construction", max_length=120)
    location: str = Field(default="", max_length=160)
    company_overview: str = Field(default="")
    potential_paint_requirements: str = Field(default="")
    project_signals: str = Field(default="")
    meeting_questions: str = Field(default="")
    next_steps: str = Field(default="")
    source_urls: str = Field(default="")

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Company name cannot be blank or empty whitespace.")
        return stripped

class BriefCreate(BriefBase):
    pass

class BriefUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=180)
    industry: str | None = None
    location: str | None = None
    company_overview: str | None = None
    potential_paint_requirements: str | None = None
    project_signals: str | None = None
    meeting_questions: str | None = None
    next_steps: str | None = None
    source_urls: str | None = None

    @field_validator("company_name")
    @classmethod
    def validate_optional_company_name(cls, v: str | None) -> str | None:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Company name cannot be blank or empty whitespace.")
            return stripped
        return v

class BriefOut(BriefBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
