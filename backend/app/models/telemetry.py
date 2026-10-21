"""Tag telemetry: deployments, raw messages as the gateway stored them, and processed tracks.

These tables sit next to the Darwin Core ones (`occurrence`, `study`) and hold the simulated
fleet (decision 0009, item_002). Every row carries `simulated` so nothing simulated can be
shown or exported as real data.
"""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Deployment(Base):
    """One tagged shark (with its Argos platform and acoustic transmitter) or one receiver."""

    __tablename__ = "deployment"
    __table_args__ = (
        UniqueConstraint("kind", "deployment_ref", name="uq_deployment_kind_ref"),
        CheckConstraint("kind IN ('shark', 'receiver')", name="ck_deployment_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    deployment_ref: Mapped[str] = mapped_column(String, nullable=False)  # shark or receiver id
    scientific_name: Mapped[str | None] = mapped_column(String)
    vernacular_name: Mapped[str | None] = mapped_column(String)
    receiver_line: Mapped[str | None] = mapped_column(String)
    argos_program: Mapped[str | None] = mapped_column(String)
    platform_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    transmitter_id: Mapped[str | None] = mapped_column(String, unique=True)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ArgosDelivery(Base):
    """One Argos-style batch file taken from the inbox, with what the gateway made of it."""

    __tablename__ = "argos_delivery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    rows_decoded: Mapped[int] = mapped_column(Integer, nullable=False)
    rows_malformed: Mapped[int] = mapped_column(Integer, nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class SatelliteFixRow(Base):
    """One Argos location as delivered. Class Z keeps the pass with no position."""

    __tablename__ = "satellite_fix"
    __table_args__ = (
        UniqueConstraint("platform_id", "fixed_at", name="uq_satellite_fix_platform_time"),
        CheckConstraint("loc_class IN ('3', '2', '1', '0', 'A', 'B', 'Z')", name="ck_loc_class"),
        CheckConstraint(
            "qc IS NULL OR qc IN ('accepted', 'speed', 'no_position')", name="ck_satellite_fix_qc"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deployment_id: Mapped[int | None] = mapped_column(ForeignKey("deployment.id"), index=True)
    program: Mapped[str] = mapped_column(String, nullable=False)
    platform_id: Mapped[int] = mapped_column(Integer, nullable=False)
    satellite: Mapped[str] = mapped_column(String, nullable=False)
    fixed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    loc_class: Mapped[str] = mapped_column(String(1), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    geom: Mapped[str | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    nb_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    battery_mv: Mapped[int] = mapped_column(Integer, nullable=False)
    transmissions_total: Mapped[int] = mapped_column(Integer, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_name: Mapped[str | None] = mapped_column(String)  # first delivery carrying it
    # Set by processing: accepted into a track, rejected by the speed filter, or no position.
    qc: Mapped[str | None] = mapped_column(String)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class AcousticDetectionRow(Base):
    __tablename__ = "acoustic_detection"
    __table_args__ = (
        UniqueConstraint(
            "receiver_id", "transmitter_id", "detected_at", name="uq_acoustic_detection"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deployment_id: Mapped[int | None] = mapped_column(ForeignKey("deployment.id"), index=True)
    receiver_id: Mapped[str] = mapped_column(String, nullable=False)
    transmitter_id: Mapped[str] = mapped_column(String, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ReceiverStatusRow(Base):
    __tablename__ = "receiver_status"
    __table_args__ = (UniqueConstraint("receiver_id", "status_at", name="uq_receiver_status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    receiver_id: Mapped[str] = mapped_column(String, nullable=False)
    status_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detections_total: Mapped[int] = mapped_column(Integer, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class TrackSegment(Base):
    """A run of accepted fixes with no gap longer than the processing gap threshold.

    A gap starts a new segment, so the map never draws a line across it. `geom` is null for a
    one-point segment.
    """

    __tablename__ = "track_segment"
    __table_args__ = (
        UniqueConstraint("platform_id", "segment_no", name="uq_track_segment_platform_no"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deployment_id: Mapped[int | None] = mapped_column(ForeignKey("deployment.id"), index=True)
    platform_id: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_no: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    point_count: Mapped[int] = mapped_column(Integer, nullable=False)
    geom: Mapped[str | None] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326))
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)


class TrackPointRow(Base):
    """One position of a processed track, with the location class and error of its fix."""

    __tablename__ = "track_point"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(
        ForeignKey("track_segment.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fix_id: Mapped[int] = mapped_column(ForeignKey("satellite_fix.id"), nullable=False)
    fixed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    loc_class: Mapped[str] = mapped_column(String(1), nullable=False)
    error_km: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)
