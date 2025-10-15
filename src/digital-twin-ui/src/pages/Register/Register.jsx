import React, { useState } from "react";
import "./Register.css";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    username: "",
    full_name: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(""); // mensagem de sucesso/erro
  const [fieldErrors, setFieldErrors] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFieldErrors({}); // limpa erros anteriores

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
        // data.detail é um array de erros ou uma string
        const errors = {};
        if (Array.isArray(data.detail)) {
          data.detail.forEach((err) => {
            const field = err.loc[err.loc.length - 1]; // último item é o campo
            errors[field] = err.msg;
          });
        } else {
          // Se for string, mostrar como mensagem geral
          setMessage(data.detail || "Erro ao registar utilizador");
        }
        setFieldErrors(errors);
        throw new Error("Erro de validação");
      }

      // sucesso
      console.log("User registered successfully!", data);
      navigate("/login");
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <h1>Criar Conta 🧑‍💻</h1>
      <form onSubmit={handleSubmit} className="register-form">
        <div className="input-wrapper">
          <input
            type="text"
            name="username"
            placeholder="Nome de utilizador"
            value={form.username}
            onChange={handleChange}
            className={fieldErrors.username ? "error-input" : ""}
            required
          />
          {fieldErrors.username && (
            <span className="error-icon" data-msg={fieldErrors.username}>
              ⚠️
            </span>
          )}
        </div>
        <div className="input-wrapper">
          <input
            type="text"
            name="full_name"
            placeholder="Nome completo"
            value={form.full_name}
            onChange={handleChange}
            className={fieldErrors.full_name ? "error-input" : ""}
            required
          />
          {fieldErrors.full_name && (
            <span className="error-icon" data-msg={fieldErrors.full_name}>
              ⚠️
            </span>
          )}
        </div>
        <div className="input-wrapper">
          <input
            type="text"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className={fieldErrors.email ? "error-input" : ""}
            required
          />
          {fieldErrors.email && (
            <span className="error-icon" data-msg={fieldErrors.email}>
              ⚠️
            </span>
          )}
        </div>
        <div className="input-wrapper">
          <input
            type="password"
            name="password"
            placeholder="Palavra-passe"
            value={form.password}
            onChange={handleChange}
            className={fieldErrors.password ? "error-input" : ""}
            required
          />
          {fieldErrors.password && (
            <span className="error-icon" data-msg={fieldErrors.password}>
              ⚠️
            </span>
          )}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      {message && <p className="error">{message}</p>}

      <p className="login-link" onClick={() => navigate("/login")}>
        Já tens conta? Faz login
      </p>
    </div>
  );
}
