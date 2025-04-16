
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { players } from '../data/players';
import './PlayerDetails.css';

const PlayerDetails = () => {
  // Grab the player id from the URL
  const { id } = useParams();
  // Find the player by matching the id (parseInt converts from string to number)
  const player = players.find((p) => p.id === parseInt(id, 10));

  if (!player) {
    return (
      <div className="player-details">
        <p>Player not found.</p>
        <Link to="/">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="player-details">
      <Link to="/">← Back to Dashboard</Link>
      <h2>{`#${player.number} ${player.name}`}</h2>
      <p><strong>Height:</strong> {player.height}</p>
      <p><strong>Year:</strong> {player.year}</p>
      <p><strong>Position:</strong> {player.position}</p>
      <p><strong>Conference:</strong> {player.conference}</p>
      <hr />
      <h3>Game Averages</h3>
      <p><strong>Points:</strong> {player.points}</p>
      <p><strong>Rebounds:</strong> {player.rebounds}</p>
      <p><strong>Assists:</strong> {player.assists}</p>
      <hr />
      <h3>Shooting Stats</h3>
      <p><strong>FG:</strong> {player.fg.made} - {player.fg.attempted} ({player.fg.pct}%)</p>
      <p><strong>3PT:</strong> {player.threePt.made} - {player.threePt.attempted} ({player.threePt.pct}%)</p>
      <p><strong>FT:</strong> {player.ft.made} - {player.ft.attempted} ({player.ft.pct}%)</p>
    </div>
  );
};

export default PlayerDetails;
