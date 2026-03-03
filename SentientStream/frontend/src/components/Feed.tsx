import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { Heart, ArrowLeft, Volume2, VolumeX, Sparkles } from 'lucide-react';
import { useInView } from 'framer-motion';

interface FeedItem {
  video_id: string;
  stream_url: string;
  thumbnail_url: string;
  title: string;
  duration: number;
  primary_mood: string;
  frontend_key?: string;
}

export default function Feed() {
  const [searchParams] = useSearchParams();
  const mood = searchParams.get('mood');
  const mode = searchParams.get('mode');
  const navigate = useNavigate();
  const [videos, setVideos] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  const bottomRef = useRef<HTMLDivElement>(null);
  const isBottomInView = useInView(bottomRef, { once: false, amount: 0.1 });

  const fetchFeed = async () => {
    try {
      let query = '';
      if (mood) query = `?mood=${mood}`;
      else if (mode) query = `?mode=${mode}`;

      // Protect against HTTP 414 URI Too Long on aggressive infinite scrolling
      const currentIds = videos.map(v => v.video_id).slice(-50).join(',');
      if (currentIds) {
        query += (query ? '&' : '?') + `seen=${currentIds}`;
      }

      const res = await api.get(`/feed${query}`);
      setVideos(prev => {
        const incomingVids = res.data.map((v: FeedItem) => ({
          ...v,
          frontend_key: v.video_id + '-' + Math.random().toString(36).substring(2, 10)
        }));

        // Allow repeated videos to physically render in the endless DOM,
        // but proactively prevent literally consecutive duplicates perfectly
        const filtered = incomingVids.filter((v: FeedItem, idx: number) => {
          if (prev.length > 0 && idx === 0 && prev[prev.length - 1].video_id === v.video_id) return false;
          return true;
        });

        return [...prev, ...filtered];
      });
    } catch (e) {
      console.error('Feed failed', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, [mood, mode]);

  useEffect(() => {
    if (isBottomInView && !loading) {
      fetchFeed();
    }
  }, [isBottomInView]);

  if (loading && videos.length === 0) return <div className="h-screen bg-black text-white flex justify-center items-center">Loading Vibes...</div>;
  if (!videos.length && !loading) return <div className="h-screen bg-black text-white flex justify-center items-center flex-col"><p>No videos found</p><button onClick={() => navigate('/home')} className="mt-4 px-6 py-2 bg-purple-600 rounded-full">Go Back</button></div>;

  return (
    <div className="h-screen w-full bg-black snap-y snap-mandatory overflow-y-scroll overflow-x-hidden relative">
      <button
        onClick={() => navigate('/home')}
        className="absolute top-4 left-4 z-50 p-3 bg-black/40 backdrop-blur-md rounded-full text-white hover:bg-black/60 transition"
      >
        <ArrowLeft size={24} />
      </button>

      {videos.map((vid) => (
        <VideoPlayer key={vid.frontend_key || vid.video_id} video={vid} />
      ))}

      {/* Invisible trigger div at the bottom for infinite scrolling */}
      <div ref={bottomRef} className="h-1 w-full bg-transparent snap-start" />
    </div>
  );
}

function VideoPlayer({ video }: { video: FeedItem }) {
  const ref = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const isInView = useInView(ref, { amount: 0.6 });
  const [isLiked, setIsLiked] = useState(false);
  const [muted, setMuted] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  const watchTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const watchSeconds = useRef(0);
  const pausedCount = useRef(0);
  const hasReplayed = useRef(false);

  useEffect(() => {
    if (isInView) {
      videoRef.current?.play().then(() => setIsPlaying(true)).catch(e => console.error("Play prevented", e));
      // Start watch duration tracking
      watchTimer.current = setInterval(() => {
        watchSeconds.current += 1;

        // Push interactions instantly every 5 seconds continuously to update insights live
        if (watchSeconds.current % 5 === 0) {
          api.post('/interactions/', {
            video_id: video.video_id,
            watch_duration: 5,
            is_liked: isLiked,
            replayed: hasReplayed.current,
            paused_count: pausedCount.current
          }).catch(() => { });
          // By logging chunks of 5s dynamically, we don't have to worry about unmount as much
          // but we leave watchSeconds continuously growing for local logic if needed
        }
      }, 1000);
    } else {
      videoRef.current?.pause();
      setIsPlaying(false);
      if (videoRef.current) videoRef.current.currentTime = 0; // reset when scrolled away
      // Record leftover watch duration when scrolling away
      let leftover = watchSeconds.current % 5;
      if (leftover > 0 && watchSeconds.current > 0) {
        api.post('/interactions/', {
          video_id: video.video_id,
          watch_duration: leftover,
          is_liked: isLiked,
          replayed: hasReplayed.current,
          paused_count: pausedCount.current
        }).catch(() => { });

        watchSeconds.current = 0;
        pausedCount.current = 0;
        hasReplayed.current = false;
      }
      if (watchTimer.current) clearInterval(watchTimer.current);
    }

    return () => {
      if (watchTimer.current) clearInterval(watchTimer.current);
      let leftover = watchSeconds.current % 5;
      if (leftover > 0 && watchSeconds.current > 0) {
        api.post('/interactions/', {
          video_id: video.video_id,
          watch_duration: leftover,
          is_liked: isLiked,
          replayed: hasReplayed.current,
          paused_count: pausedCount.current
        }).catch(() => { });
        watchSeconds.current = 0;
      }
    }
  }, [isInView, video.video_id, isLiked]);

  const handleLike = () => {
    const newStatus = !isLiked;
    setIsLiked(newStatus);
    api.post('/interactions/', {
      video_id: video.video_id,
      watch_duration: 0,
      is_liked: newStatus,
      replayed: false,
      paused_count: 0
    }).catch(() => { });
  };

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
        pausedCount.current += 1; // user manually paused
      } else {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleEnded = () => {
    hasReplayed.current = true;
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
    }
  };

  return (
    <div ref={ref} className="h-screen w-full snap-start snap-always relative bg-zinc-900 flex justify-center items-center">
      <video
        ref={videoRef}
        src={video.stream_url}
        poster={video.thumbnail_url}
        className="absolute inset-0 w-full h-full object-cover"
        playsInline
        muted={muted}
        onEnded={handleEnded}
        onClick={togglePlayPause}
      />

      {/* Overlays */}
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-6 pt-32 pb-8 flex justify-between items-end pointer-events-none">

        <div className="flex-1 pr-12 text-white pointer-events-auto">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1">
              <Sparkles size={12} /> {video.primary_mood}
            </span>
          </div>
          <h2 className="text-lg font-bold line-clamp-2">{video.title || "SentientStream Video"}</h2>
        </div>

        <div className="flex flex-col items-center gap-6 pb-4 pointer-events-auto">
          <button
            onClick={handleLike}
            className="group flex flex-col items-center gap-1 transition-transform active:scale-90"
          >
            <div className={`p-3 rounded-full bg-black/40 backdrop-blur-md ${isLiked ? 'text-pink-500' : 'text-white'}`}>
              <Heart size={28} className={isLiked ? "fill-current" : ""} />
            </div>
            <span className="text-white text-xs font-medium">{isLiked ? 'Liked' : 'Like'}</span>
          </button>

          <button
            onClick={() => setMuted(!muted)}
            className="p-3 rounded-full bg-black/40 backdrop-blur-md text-white transition-opacity hover:bg-black/60"
          >
            {muted ? <VolumeX size={24} /> : <Volume2 size={24} />}
          </button>
        </div>
      </div>
    </div>
  );
}
