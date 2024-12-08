from app.config.database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Transcriptions(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    upload_uuid = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    transcription_text = Column(Text, nullable=True)
    context = Column(JSON, nullable=False, default={})
    status = Column(String(255), nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("Users", back_populates="transcriptions")
    form = relationship("Forms", back_populates="transcriptions")
