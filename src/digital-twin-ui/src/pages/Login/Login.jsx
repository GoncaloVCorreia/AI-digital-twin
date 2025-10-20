import React, { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({
    username: "",
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
      const body = new URLSearchParams();
      body.append("username", form.username);
      body.append("password", form.password);

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
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
      <h1>Bem-vindo de volta 👋</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <input
          type="text"
          name="username"
          placeholder="Nome de utilizador"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Palavra-passe"
          value={form.password}
          onChange={handleChange}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "A entrar..." : "Entrar"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p className="register-link" onClick={() => navigate("/register")}>
        Ainda não tens conta? Regista-te
      </p>
    </div>
  );
}
