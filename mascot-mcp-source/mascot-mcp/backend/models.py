from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class CompanyBrief(Base):
    __tablename__ = "company_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    industry: Mapped[str] = mapped_column(String(120), default="Paint / Construction")
    location: Mapped[str] = mapped_column(String(160), default="")
    company_overview: Mapped[str] = mapped_column(Text, default="")
    potential_paint_requirements: Mapped[str] = mapped_column(Text, default="")
    project_signals: Mapped[str] = mapped_column(Text, default="")
    meeting_questions: Mapped[str] = mapped_column(Text, default="")
    next_steps: Mapped[str] = mapped_column(Text, default="")
    source_urls: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
