import React, { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../../contexts/ThemeContext";

export default function Login() {
  const { darkMode, toggleDarkMode } = useTheme();
  const [form, setForm] = useState({
    username: "",
    password: "",
    secret_key: "",
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
      const body = new URLSearchParams();
      body.append("username", form.username);
      body.append("password", form.password);

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": `Bearer ${form.secret_key}`,
          },
          body: body.toString(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erro no login");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("username", form.username);
      localStorage.setItem("id", data.id);
      
      console.log("Login bem-sucedido:", data);

      navigate("/");

    } catch (err) {
      console.error("Erro:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <button 
        className="theme-toggle-btn" 
        onClick={toggleDarkMode}
        title={darkMode ? "Light Mode" : "Dark Mode"}
      >
        {darkMode ? "☀️" : "🌙"}
      </button>
      <h1>Welcome Back 👋</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
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
        <input
          type="password"
          name="secret_key"
          placeholder="Secret Key"
          value={form.secret_key}
          onChange={handleChange}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Loggin in..." : "Log In"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p className="register-link" onClick={() => navigate("/register")}>
        Don't have an account? Sign up
      </p>
    </div>
  );
}
