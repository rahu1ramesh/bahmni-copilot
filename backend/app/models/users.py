from app.db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, default="")
    encrypted_password = Column(String, nullable=False, default="")
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    admin = Column(Boolean, default=False)

    transcriptions = relationship("Transcriptions", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<User(id={self.id}, email='{self.email}', admin={self.admin}, "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}')>")
