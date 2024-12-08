from app.config.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String(255)(255), nullable=False)
    user_name = Column(String(255), unique=True, nullable=False, default="")
    email = Column(String(255), unique=True, nullable=False, default="")
    password = Column(String(255), nullable=False, default="")
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    is_admin = Column(Boolean, default=False)

    transcriptions = relationship("Transcriptions", back_populates="user", cascade="all, delete-orphan")
