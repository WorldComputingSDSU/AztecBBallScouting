// StatsTable.js
import React from "react";
import "./StatsTable.css";

const StatsTable = ({ players }) => {
  return (
    <div className="stats-table-wrapper">
      <table className="stats-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Height / Class</th>
            <th>Pts / Reb / Ast</th>
            <th>FG</th>
            <th>3PT</th>
            <th>FT</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player) => (
            <tr key={player.id}>
              <td className="player-name">
                <span className="number">#{player.number}</span> {player.name}
              </td>
              <td>
                {player.height} {player.year}
              </td>
              <td>{`${player.points} / ${player.rebounds} / ${player.assists}`}</td>
              <td className="player-shooting">
                {player.fg.made}-{player.fg.attempted}
                <div className="pct">{player.fg.pct}%</div>
              </td>
              <td className="player-shooting">
                {player.threePt.made}-{player.threePt.attempted}
                <div className="pct">{player.threePt.pct}%</div>
              </td>
              <td className="player-shooting">
                {player.ft.made}-{player.ft.attempted}
                <div className="pct">{player.ft.pct}%</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatsTable;
