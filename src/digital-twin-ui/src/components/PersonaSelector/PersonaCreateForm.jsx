import React, { useState } from "react";
import { createNewPersona } from "../../api/chatApi";

export default function PersonaCreateForm({ onCreated, onCancel }) {
  const [form, setForm] = useState({
    name: "",
    age: "",
    location: "",
    description: "",
    education: "",
    tech_skills: "",
    soft_skills: "",
    strenghts: "",
    weaknesses: "",
    goals: "",
    hobbies: "",
    personality: "",
    data_path: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await createNewPersona(
        form.name,
        Number(form.age),
        form.location,
        form.description,
        form.education,
        form.tech_skills,
        form.soft_skills,
        form.strenghts,
        form.weaknesses,
        form.goals,
        form.hobbies,
        form.personality,
        form.data_path
      );
      setLoading(false);
      if (onCreated) onCreated();
    } catch (err) {
      setError(err.message || "Erro ao criar persona.");
      setLoading(false);
    }
  }

  // Divide os campos em duas colunas
  const leftFields = [
    "name",
    "age",
    "location",
    "description",
    "education",
    "tech_skills",
    "data_path",
  ];
  const rightFields = [
    "soft_skills",
    "strenghts",
    "weaknesses",
    "goals",
    "hobbies",
    "personality",
  ];

  return (
    <form
      className="persona-create-form"
      onSubmit={handleSubmit}
    >
      <h2 style={{ textAlign: "center", marginBottom: 16, color: "var(--text-primary)" }}>Nova Persona</h2>
      <div className="persona-create-form-fields" style={{ display: "flex", gap: "24px", width: "100%" }}>
        <div className="persona-create-form-col" style={{ flex: 1, marginRight: 12 }}>
          {leftFields.map((key) => (
            <div key={key} style={{ marginBottom: 12 }}>
              <label
                style={{
                  fontWeight: 500,
                  display: "block",
                  marginBottom: 4,
                  color: "var(--text-primary)",
                }}
              >
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </label>
              <input
                type={key === "age" ? "number" : "text"}
                name={key}
                value={form[key]}
                onChange={handleChange}
                required={key === "name" || key === "age"}
                style={{
                  width: "100%",
                  padding: "8px",
                  borderRadius: 6,
                  border: "1px solid var(--border-color)",
                  background: "var(--input-bg)",
                  color: "var(--text-primary)",
                }}
              />
            </div>
          ))}
        </div>
        <div className="persona-create-form-col" style={{ flex: 1 }}>
          {rightFields.map((key) => (
            <div key={key} style={{ marginBottom: 12 }}>
              <label
                style={{
                  fontWeight: 500,
                  display: "block",
                  marginBottom: 4,
                  color: "var(--text-primary)",
                }}
              >
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </label>
              <input
                type="text"
                name={key}
                value={form[key]}
                onChange={handleChange}
                required={false}
                style={{
                  width: "100%",
                  padding: "8px",
                  borderRadius: 6,
                  border: "1px solid var(--border-color)",
                  background: "var(--input-bg)",
                  color: "var(--text-primary)",
                }}
              />
            </div>
          ))}
        </div>
      </div>
      {error && <div style={{ color: "#e74c3c", marginBottom: 8 }}>{error}</div>}
      <div
        style={{
          display: "flex",
          gap: 12,
          justifyContent: "center",
          marginTop: 18,
        }}
      >
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "8px 18px",
            borderRadius: 8,
            background: "#3a8bfd",
            color: "#fff",
            border: "none",
            fontWeight: 600,
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "1rem",
            transition: "background 0.2s",
            opacity: loading ? 0.6 : 1,
          }}
          onMouseEnter={(e) => !loading && (e.target.style.background = "#0056b3")}
          onMouseLeave={(e) => !loading && (e.target.style.background = "#3a8bfd")}
        >
          {loading ? "A criar..." : "Criar"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: "8px 18px",
            borderRadius: 8,
            background: "var(--bg-tertiary)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-color)",
            fontWeight: 600,
            cursor: "pointer",
            fontSize: "1rem",
            transition: "background 0.2s",
          }}
          onMouseEnter={(e) => (e.target.style.background = "var(--border-color)")}
          onMouseLeave={(e) => (e.target.style.background = "var(--bg-tertiary)")}
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
