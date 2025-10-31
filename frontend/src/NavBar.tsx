import React from 'react';
import { NavLink } from 'react-router-dom';
import './NavBar.css';

const NavBar: React.FC = () => {
    return (
        <nav className="navbar">
            <div className="nav-container">
                <NavLink to="/" className="nav-logo">
                    CryptoTrader
                </NavLink>
                <ul className="nav-menu">
                    <li className="nav-item">
                        <NavLink to="/" className={({ isActive }) => "nav-links" + (isActive ? " activated" : "")}>
                            Dashboard
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/bots" className={({ isActive }) => "nav-links" + (isActive ? " activated" : "")}>
                            Bot Management
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/history" className={({ isActive }) => "nav-links" + (isActive ? " activated" : "")}>
                            Trade History
                        </NavLink>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default NavBar;
