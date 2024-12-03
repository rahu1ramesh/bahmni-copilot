from app.db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Forms(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    transcriptions = relationship("Transcriptions", back_populates="form", cascade="all, delete-orphan")

    # Relationship with Fields
    fields = relationship(
        "Fields",
        back_populates="form",
        cascade="all, delete-orphan",
        lazy="joined",  # Optional for optimization
    )

    def __repr__(self):
        return (f"<Forms(id={self.id}, name='{self.name}', prompt='{self.prompt}', "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}')>")
