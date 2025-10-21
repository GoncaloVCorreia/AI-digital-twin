import React, { useState } from "react";
import "./Register.css";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../../contexts/ThemeContext";

export default function Register() {
  const { darkMode, toggleDarkMode } = useTheme();
  const [form, setForm] = useState({
    username: "",
    full_name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(form),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || "Erro no registo");
      }

      console.log("Registo bem-sucedido:", data);
      navigate("/login");
    } catch (err) {
      console.error("Erro:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <button
        className="theme-toggle-btn"
        onClick={toggleDarkMode}
        title={darkMode ? "Light Mode" : "Dark Mode"}
      >
        {darkMode ? "☀️" : "🌙"}
      </button>
      <h1>Create Account</h1>
      <form onSubmit={handleSubmit} className="register-form">
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="full_name"
          placeholder="Full name"
          value={form.name}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p className="login-link" onClick={() => navigate("/login")}>
        Already have an account? Log in
      </p>
    </div>
  );
}
