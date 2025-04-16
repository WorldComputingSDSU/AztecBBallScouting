
import React from 'react';
import './Sidebar.css';

const Sidebar = ({ filters, onFilterChange }) => {
  const handleSelect = (event) => {
    const { name, value } = event.target;
    // Update filters object 
    onFilterChange({ ...filters, [name]: value });
  };

  return (
    <aside className="sidebar">
      <h2>Filters</h2>

      <div className="filter-group">
        <label htmlFor="yearSelect">Year:</label>
        <select
          name="year"
          id="yearSelect"
          value={filters.year}
          onChange={handleSelect}
        >
          <option value="All">All</option>
          <option value="Sr">Sr</option>
          <option value="Jr">Jr</option>
          <option value="So">So</option>
          <option value="Fr">Fr</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="positionSelect">Position:</label>
        <select
          name="position"
          id="positionSelect"
          value={filters.position}
          onChange={handleSelect}
        >
          <option value="All">All</option>
          <option value="Guard">Guard</option>
          <option value="Forward">Forward</option>
          <option value="Center">Center</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="conferenceSelect">Conference:</label>
        <select
          name="conference"
          id="conferenceSelect"
          value={filters.conference}
          onChange={handleSelect}
        >
          <option value="All">All</option>
          <option value="In-Conference">In-Conference</option>
          <option value="Non-Conference">Non-Conference</option>
        </select>
      </div>
    </aside>
  );
};

export default Sidebar;
