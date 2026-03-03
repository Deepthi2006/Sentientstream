import { Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from './context/AuthContext';
import Login from './components/Login';
import Signup from './components/Signup';
import Home from './components/Home';
import Feed from './components/Feed';

function App() {
  const { token } = useContext(AuthContext);

  return (
    <Routes>
      <Route path="/" element={<Navigate to={token ? "/home" : "/login"} />} />
      <Route path="/login" element={token ? <Navigate to="/home" /> : <Login />} />
      <Route path="/signup" element={token ? <Navigate to="/home" /> : <Signup />} />
      <Route path="/home" element={token ? <Home /> : <Navigate to="/login" />} />
      <Route path="/feed" element={token ? <Feed /> : <Navigate to="/login" />} />
    </Routes>
  );
}

export default App;
