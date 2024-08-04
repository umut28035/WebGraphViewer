import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GraphViewer from './GraphViewer';
import WelcomePage from './WelcomePage';
import Tutorial from './Tutorial';
import Navbar from './Navbar';


const App = () => {
  return (
    <Router>
         <Navbar />
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/graph-viewer" element={<GraphViewer />} />
          <Route path="/tutorial" element={<Tutorial />} />
        </Routes>
    </Router>
  );
};

export default App;
