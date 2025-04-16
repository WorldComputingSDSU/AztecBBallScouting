import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import PlayerDetails from './components/PlayerDetails';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/player/:id" element={<PlayerDetails />} />
    </Routes>
  );
}

export default App;
