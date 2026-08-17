from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Occurrence(Base):
    """A Darwin Core Occurrence record (species observation/detection).

    Column names follow Darwin Core terms (see docs/research/03-data-standards.md) so records
    stay traceable to their source field, even though this table holds occurrences from multiple
    datasets/sources over time, not just the initial whale shark ingestion.
    """

    __tablename__ = "occurrence"
    __table_args__ = (UniqueConstraint("occurrence_id", name="uq_occurrence_occurrence_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    occurrence_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    dataset_id: Mapped[str | None] = mapped_column(String)
    dataset_name: Mapped[str | None] = mapped_column(String)
    basis_of_record: Mapped[str | None] = mapped_column(String)

    scientific_name: Mapped[str | None] = mapped_column(String, index=True)
    vernacular_name: Mapped[str | None] = mapped_column(String)

    event_date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    decimal_latitude: Mapped[float | None] = mapped_column(Float)
    decimal_longitude: Mapped[float | None] = mapped_column(Float)
    coordinate_uncertainty_in_meters: Mapped[float | None] = mapped_column(Float)

    individual_count: Mapped[int | None] = mapped_column(Integer)
    sex: Mapped[str | None] = mapped_column(String)
    life_stage: Mapped[str | None] = mapped_column(String)
    occurrence_status: Mapped[str | None] = mapped_column(String)
    organism_id: Mapped[str | None] = mapped_column(String)

    license: Mapped[str | None] = mapped_column(String)
    rights_holder: Mapped[str | None] = mapped_column(String)
    bibliographic_citation: Mapped[str | None] = mapped_column(String)

    geom: Mapped[str | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
