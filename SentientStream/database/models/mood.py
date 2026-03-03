import uuid
from sqlalchemy import Column, String, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


class VideoMood(Base):
    __tablename__ = "video_moods"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id          = Column(UUID(as_uuid=True),
                               ForeignKey("videos.id", ondelete="CASCADE"),
                               nullable=False, unique=True)
    primary_mood      = Column(String(50), nullable=False)
    mood_scores       = Column(JSONB)          # {"happy": 0.85, "calm": 0.10, ...}
    scene_description = Column(Text)
    analysis_text     = Column(Text)           # raw Groq response
    model_used        = Column(String(100))
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="mood")

    def __repr__(self):
        return f"<VideoMood video_id={self.video_id} mood={self.primary_mood}>"
