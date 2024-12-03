from app.config.database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Transcriptions(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    upload_uuid = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    transcription_text = Column(Text, nullable=True)
    context = Column(JSON, nullable=False, default={})
    status = Column(String, nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("Users", back_populates="transcriptions")
    form = relationship("Forms", back_populates="transcriptions")

    def __repr__(self):
        return (
            f"<Transcription(id={self.id}, user_id={self.user_id}, form_id={self.form_id}, "
            f"status='{self.status}', duration={self.duration}, total_tokens={self.total_tokens}, "
            f"created_at='{self.created_at}', updated_at='{self.updated_at}')>"
        )
