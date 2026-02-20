from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String, index=True)
    brand: Mapped[str | None] = mapped_column(String, index=True)
    address: Mapped[str | None] = mapped_column(Text)

    geog: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(String)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
