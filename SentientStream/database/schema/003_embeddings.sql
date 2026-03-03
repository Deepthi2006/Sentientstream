-- ─────────────────────────────────────────────────────────────────────────────
-- video_embeddings: links each video to its FAISS vector index position
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS video_embeddings (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id         UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    faiss_index_id   INTEGER NOT NULL,          -- row position inside FAISS flat index
    embedding_model  VARCHAR(100) NOT NULL,     -- e.g. all-MiniLM-L6-v2
    embedding_dim    INTEGER NOT NULL,          -- 384 for MiniLM
    embedded_text    TEXT,                      -- the text string that was embedded
    created_at       TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_video_embedding UNIQUE (video_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_video_embeddings_video_id  ON video_embeddings(video_id);
CREATE INDEX IF NOT EXISTS idx_video_embeddings_faiss_id  ON video_embeddings(faiss_index_id);
