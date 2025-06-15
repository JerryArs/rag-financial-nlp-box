import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import NERPage from './pages/NERPage';
import StdPage from './pages/StdPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <div className="flex-1 overflow-auto">
          <Routes>
            <Route path="/ner" element={<NERPage />} />
            <Route path="/std" element={<StdPage />} />
            <Route path="/" element={<NERPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;