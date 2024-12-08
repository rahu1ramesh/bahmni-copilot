from app.config.database import Base
from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Fields(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    query_selector = Column(String, nullable=True)
    description = Column(String, nullable=True)
    field_type = Column(String, nullable=False, default="string")
    minimum = Column(Float, nullable=True)
    maximum = Column(Float, nullable=True)
    enum_options = Column(String, nullable=True)
    form_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    form = relationship("Forms", back_populates="fields")
