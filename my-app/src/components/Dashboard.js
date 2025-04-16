// Dashboard
import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import PlayerCard from './PlayerCard';
import StatsTable from './StatsTable';
import './Dashboard.css';
import { players as initialPlayers } from '../data/players';



export default function Dashboard() {
  const [players] = useState(initialPlayers);
  const [filters, setFilters] = useState({
    year: "All",
    position: "All",
    conference: "All"
  });
  const [sortOption, setSortOption] = useState('number');

  const filteredPlayers = players.filter((player) => {
    const matchYear = filters.year === "All" || player.year === filters.year;
    const matchPosition = filters.position === "All" || player.position === filters.position;
    const matchConference = filters.conference === "All" || player.conference === filters.conference;
    return matchYear && matchPosition && matchConference;
  });

  const sortedPlayers = [...filteredPlayers].sort((a, b) => {
    switch (sortOption) {
      case 'points':
        return b.points - a.points;
      case 'rebounds':
        return b.rebounds - a.rebounds;
      case 'assists':
        return b.assists - a.assists;
      default:
        return a.number - b.number;
    }
  });

  return (
    <div className="dashboard">
      <Header />
      <div className="main-container">
        <Sidebar filters={filters} onFilterChange={setFilters} />
        <main className="content">
          <h2>Player Stats {filters.year !== "All" && `- ${filters.year}`}</h2>
          <div style={{ marginBottom: "1rem" }}>
            <select value={sortOption} onChange={(e) => setSortOption(e.target.value)}>
              <option value="number">Sort by Number</option>
              <option value="points">Sort by Points</option>
              <option value="rebounds">Sort by Rebounds</option>
              <option value="assists">Sort by Assists</option>
            </select>
          </div>
          <StatsTable players={sortedPlayers} />
          <div className="cards-container">
            {sortedPlayers.map((player) => (
              <PlayerCard key={player.id} player={player} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
