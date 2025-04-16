//  Header.js
import React from 'react';
import { NavLink } from 'react-router-dom';  // Import NavLink
import './Header.css';

const Header = () => (
  <header className="header">
    <div className="header-container">
      {}
      <img src="/logo/logo.png" alt="SDSU Logo" className="logo" />
      <h1>SDSU Men's Basketball Scouting</h1>
      <nav>
        <ul className="nav-links">
          <li>
            <NavLink 
              to="/" 
              className={({ isActive }) => isActive ? 'active-link' : ''}
              end>
              Home
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/reports" 
              className={({ isActive }) => isActive ? 'active-link' : ''}>
              Reports
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/settings" 
              className={({ isActive }) => isActive ? 'active-link' : ''}>
              Settings
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  </header>
);

export default Header;

