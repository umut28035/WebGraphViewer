import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="border-black-900 p-4 fixed top-0 left-0 right-0 z-50 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <img src="/logo.png" alt="Logo" className="w-8 h-8" />
          <div className="text-white text-xl font-semibold">IP URL GRAPH</div>
        </div>
        <div className="flex space-x-6">
          <Link to="/" className="text-gray-300 hover:text-white transition-colors duration-300">Home</Link>
          <Link to="/tutorial" className="text-gray-300 hover:text-white transition-colors duration-300">Tutorial</Link>
          <Link to="/graph-viewer" className="text-gray-300 hover:text-white transition-colors duration-300">Graph Viewer</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
