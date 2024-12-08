from app.config.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Forms(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    prompt = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    transcriptions = relationship("Transcriptions", back_populates="form", cascade="all, delete-orphan")

    fields = relationship(
        "Fields",
        back_populates="form",
        cascade="all, delete-orphan",
        lazy="joined",
    )
