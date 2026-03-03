import uuid
from sqlalchemy import Column, String, Integer, Float, Text, BigInteger, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from database.connection import Base


class Video(Base):
    __tablename__ = "videos"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pexels_id     = Column(BigInteger, unique=True, nullable=False)
    title         = Column(Text)
    description   = Column(Text)
    duration      = Column(Integer)           # seconds
    width         = Column(Integer)
    height        = Column(Integer)
    fps           = Column(Float)
    local_path    = Column(Text)              # absolute path to .mp4 on disk
    thumbnail_url = Column(Text)
    tags          = Column(ARRAY(String))
    author        = Column(String(255))
    source_url    = Column(Text)
    file_size     = Column(BigInteger)        # bytes
    status        = Column(String(20), nullable=False, default="pending")
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now())

    # One-to-one relationships
    mood      = relationship("VideoMood",      back_populates="video",
                             uselist=False, cascade="all, delete-orphan")
    embedding = relationship("VideoEmbedding", back_populates="video",
                             uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video pexels_id={self.pexels_id} status={self.status}>"
