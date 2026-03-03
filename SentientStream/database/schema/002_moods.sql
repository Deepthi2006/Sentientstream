-- ─────────────────────────────────────────────────────────────────────────────
-- video_moods: AI-detected mood classification per video
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS video_moods (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id          UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    primary_mood      VARCHAR(50) NOT NULL,
                      -- one of: happy | sad | energetic | calm
                      --         romantic | dark | inspirational | funny
    mood_scores       JSONB,
                      -- {"happy": 0.85, "calm": 0.10, "sad": 0.05, ...}
    scene_description TEXT,                    -- AI visual scene summary
    analysis_text     TEXT,                    -- raw Groq response (debug)
    model_used        VARCHAR(100),            -- e.g. llama-3.2-11b-vision-preview
    created_at        TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_video_mood UNIQUE (video_id)  -- one mood record per video
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_video_moods_video_id     ON video_moods(video_id);
CREATE INDEX IF NOT EXISTS idx_video_moods_primary_mood ON video_moods(primary_mood);
