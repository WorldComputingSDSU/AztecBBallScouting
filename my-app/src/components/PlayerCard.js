// PlayerCard component to display individual player stats and link to their profile page
import React from 'react';
import { Link } from 'react-router-dom';
import './PlayerCard.css';

const PlayerCard = ({ player }) => (
  <Link to={`/player/${player.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
    <div className="player-card">
      <h3>{`#${player.number} ${player.name}`}</h3>
      <p className="player-info">{`${player.height} | ${player.year}`}</p>
      <div className="stats">
        <p>{`Points: ${player.points} | Rebounds: ${player.rebounds} | Assists: ${player.assists}`}</p>
        <div className="shooting-stats">
          <p><strong>FG:</strong> {player.fg.made}-{player.fg.attempted} ({player.fg.pct}%)</p>
          <p><strong>3PT:</strong> {player.threePt.made}-{player.threePt.attempted} ({player.threePt.pct}%)</p>
          <p><strong>FT:</strong> {player.ft.made}-{player.ft.attempted} ({player.ft.pct}%)</p>
        </div>
      </div>
    </div>
  </Link>
);

export default PlayerCard;
