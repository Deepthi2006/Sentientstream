import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.connection import Base


class VideoEmbedding(Base):
    __tablename__ = "video_embeddings"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id        = Column(UUID(as_uuid=True),
                             ForeignKey("videos.id", ondelete="CASCADE"),
                             nullable=False, unique=True)
    faiss_index_id  = Column(Integer, nullable=False)  # row position in FAISS index
    embedding_model = Column(String(100), nullable=False)
    embedding_dim   = Column(Integer, nullable=False)
    embedded_text   = Column(Text)                     # text used to generate vector
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="embedding")

    def __repr__(self):
        return f"<VideoEmbedding video_id={self.video_id} faiss_id={self.faiss_index_id}>"
