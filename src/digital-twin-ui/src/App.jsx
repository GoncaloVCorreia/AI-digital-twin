import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage/HomePage";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import ChatView from "./pages/ChatView/ChatView";
import PrivateRoute from "./components/PrivateRoute";

function App() {
  // Clear all authentication tokens when app starts
  useEffect(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
  }, []); // Empty dependency array means this runs once on mount

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <ChatView />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
