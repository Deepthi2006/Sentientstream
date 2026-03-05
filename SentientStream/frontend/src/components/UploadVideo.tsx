import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Upload, FileVideo, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import api from '../api';
import BottomNav from './BottomNav';

export default function UploadVideo() {
    const navigate = useNavigate();
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const [detectedMood, setDetectedMood] = useState('');

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (selectedFile.type !== 'video/mp4') {
                setError('Only .mp4 videos are supported at this time.');
                return;
            }
            setFile(selectedFile);
            setError('');
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await api.post('/upload/video', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setSuccess(true);
            setDetectedMood(res.data.mood);
            setUploading(false);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
            setUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center min-h-screen bg-black text-zinc-100 relative pb-24">
            <div className="w-full max-w-md p-6">
                {/* Header */}
                <div className="flex items-center gap-4 mb-10 pt-4">
                    <button onClick={() => navigate('/home')} className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Upload className="text-green-500" />
                        Upload Video
                    </h1>
                </div>

                {success ? (
                    <div className="flex flex-col items-center justify-center space-y-6 py-12 animate-in fade-in zoom-in duration-500">
                        <div className="p-4 bg-green-500/10 rounded-full border border-green-500/20">
                            <CheckCircle2 className="text-green-500" size={64} />
                        </div>
                        <div className="text-center space-y-2">
                            <h2 className="text-2xl font-black uppercase tracking-wider">Sync Successful</h2>
                            <p className="text-zinc-400 text-sm">Your frequency has been analyzed.</p>
                        </div>

                        <div className="bg-[#0a0a0a] border border-zinc-800 p-6 rounded-2xl w-full text-center">
                            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Detected Vibe</span>
                            <div className="mt-2 text-xl font-black text-green-400 uppercase tracking-widest">
                                {detectedMood}
                            </div>
                        </div>

                        <button
                            onClick={() => navigate('/home')}
                            className="w-full py-4 bg-white text-black font-black uppercase tracking-widest rounded-xl hover:scale-[1.02] active:scale-95 transition"
                        >
                            Return to Matrix
                        </button>
                    </div>
                ) : (
                    <div className="space-y-8">
                        <div
                            className={`border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center gap-4 transition-all duration-300 ${file ? 'border-green-500/50 bg-green-500/5' : 'border-zinc-800 bg-zinc-900/20 hover:border-zinc-700'
                                }`}
                        >
                            <input
                                type="file"
                                accept="video/mp4"
                                onChange={handleFileChange}
                                className="hidden"
                                id="video-upload"
                            />
                            <label htmlFor="video-upload" className="cursor-pointer flex flex-col items-center gap-4">
                                {file ? (
                                    <FileVideo className="text-green-500" size={48} />
                                ) : (
                                    <Upload className="text-zinc-600" size={48} />
                                )}
                                <div className="text-center">
                                    <p className="font-bold text-sm tracking-wide">
                                        {file ? file.name : 'Tap to select video'}
                                    </p>
                                    <p className="text-xs text-zinc-500 mt-1">MP4 format only</p>
                                </div>
                            </label>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex gap-3 items-center">
                                <AlertCircle className="text-red-500 shrink-0" size={18} />
                                <p className="text-xs text-red-200 font-medium">{error}</p>
                            </div>
                        )}

                        <button
                            disabled={!file || uploading}
                            onClick={handleUpload}
                            className={`w-full py-4 rounded-2xl font-black uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all ${!file || uploading
                                    ? 'bg-zinc-900 text-zinc-600 cursor-not-allowed'
                                    : 'bg-green-600 text-white hover:bg-green-500 shadow-lg shadow-green-900/20'
                                }`}
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Analyzing Neural Matrix...
                                </>
                            ) : (
                                <>
                                    <Upload size={20} />
                                    Initiate Sync
                                </>
                            )}
                        </button>

                        <div className="bg-[#050505] border border-zinc-800/50 p-6 rounded-2xl">
                            <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 text-center">AI Vision Protocol</h4>
                            <p className="text-[10px] text-zinc-600 leading-relaxed text-center italic">
                                Each upload is processed by the SentientStream vision model.
                                Frames are extracted and analyzed mathematically for emotional resonance
                                before being injected into the global recommendation cluster.
                            </p>
                        </div>
                    </div>
                )}
            </div>
            <BottomNav />
        </div>
    );
}
