-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- videos: stores all video metadata + local file path
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS videos (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pexels_id       BIGINT UNIQUE NOT NULL,
    title           TEXT,
    description     TEXT,
    duration        INTEGER,                    -- seconds
    width           INTEGER,
    height          INTEGER,
    fps             FLOAT,
    local_path      TEXT,                       -- absolute path to .mp4 on disk
    thumbnail_url   TEXT,                       -- pexels preview image URL
    tags            TEXT[],                     -- search tags used
    author          VARCHAR(255),               -- pexels uploader name
    source_url      TEXT,                       -- pexels page URL
    file_size       BIGINT,                     -- bytes
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
                                                -- pending | downloading | downloaded
                                                -- processing | ready | failed
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_videos_status    ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_pexels_id ON videos(pexels_id);

-- Auto-update updated_at on every row change
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS videos_updated_at ON videos;
CREATE TRIGGER videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
