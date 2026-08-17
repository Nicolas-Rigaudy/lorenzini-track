from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Study(Base):
    """A source dataset/research study (e.g. one Darwin Core Archive), independent of any
    single occurrence record - holds the metadata needed for "study exploration mode":
    what it is, who published it, and where to read more.
    """

    __tablename__ = "study"

    id: Mapped[int] = mapped_column(primary_key=True)

    dataset_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[str | None] = mapped_column(String)
    data_provider: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String)
    license: Mapped[str | None] = mapped_column(String)
    rights_holder: Mapped[str | None] = mapped_column(String)
    published_date: Mapped[date | None] = mapped_column(Date)

    occurrences: Mapped[list["Occurrence"]] = relationship(back_populates="study")  # noqa: F821
