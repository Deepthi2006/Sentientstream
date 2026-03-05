import { Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from './context/AuthContext';
import Login from './components/Login';
import Signup from './components/Signup';
import Home from './components/Home';
import Feed from './components/Feed';
import Insights from './components/Insights';
import WeeklySummary from './components/WeeklySummary';
import AiCoach from './components/AiCoach';
import TheVault from './components/TheVault';
import NexusSession from './components/NexusSession';
import UploadVideo from './components/UploadVideo';

function App() {
  const { token } = useContext(AuthContext);

  return (
    <div className="bg-zinc-950 min-h-screen flex justify-center overflow-x-hidden">
      <div className="w-full max-w-md bg-black min-h-screen shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-y-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/signup" />} />
          <Route path="/login" element={token ? <Navigate to="/home" /> : <Login />} />
          <Route path="/signup" element={token ? <Navigate to="/home" /> : <Signup />} />
          <Route path="/home" element={token ? <Home /> : <Navigate to="/login" />} />
          <Route path="/feed" element={token ? <Feed /> : <Navigate to="/login" />} />
          <Route path="/insights" element={token ? <Insights /> : <Navigate to="/login" />} />
          <Route path="/weekly-summary" element={token ? <WeeklySummary /> : <Navigate to="/login" />} />
          <Route path="/ai-coach" element={token ? <AiCoach /> : <Navigate to="/login" />} />
          <Route path="/upload" element={token ? <UploadVideo /> : <Navigate to="/login" />} />
          <Route path="/vault" element={token ? <TheVault /> : <Navigate to="/login" />} />
          <Route path="/nexus" element={token ? <NexusSession /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
