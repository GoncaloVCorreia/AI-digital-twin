import React, { useState, useEffect } from "react";
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

  // Add avatar selection state
  const [selectedAvatarIndex, setSelectedAvatarIndex] = useState(0);
  const [availableAvatars, setAvailableAvatars] = useState([]);
  const [loadingAvatars, setLoadingAvatars] = useState(true);

  // Automatically detect available avatars
  useEffect(() => {
    async function detectAvatars() {
      const detectedAvatars = [];
      let index = 1;
      let consecutiveFails = 0;
      const maxConsecutiveFails = 3; // Stop after 3 consecutive missing avatars

      while (consecutiveFails < maxConsecutiveFails) {
        const avatarName = `Avatar_${index}`;
        const avatarPath = `/avatars/${avatarName}.png`;
        
        try {
          // Try to load the image
          const exists = await checkImageExists(avatarPath);
          if (exists) {
            detectedAvatars.push(avatarName);
            consecutiveFails = 0; // Reset counter on success
          } else {
            consecutiveFails++;
          }
        } catch {
          consecutiveFails++;
        }
        
        index++;
        
        // Safety limit to prevent infinite loop
        if (index > 100) break;
      }

      console.log(`Detected ${detectedAvatars.length} avatars:`, detectedAvatars);
      setAvailableAvatars(detectedAvatars.length > 0 ? detectedAvatars : ["default"]);
      setLoadingAvatars(false);
    }

    detectAvatars();
  }, []);

  // Helper function to check if image exists
  function checkImageExists(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = url;
    });
  }

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
        form.data_path,
        availableAvatars[selectedAvatarIndex] // Pass the selected avatar
      );
      setLoading(false);
      if (onCreated) onCreated();
    } catch (err) {
      setError(err.message || "Erro ao criar persona.");
      setLoading(false);
    }
  }

  const handlePrevAvatar = () => {
    setSelectedAvatarIndex((prev) => 
      prev === 0 ? availableAvatars.length - 1 : prev - 1
    );
  };

  const handleNextAvatar = () => {
    setSelectedAvatarIndex((prev) => 
      prev === availableAvatars.length - 1 ? 0 : prev + 1
    );
  };

  const handleImageError = (e) => {
    e.target.src = '/avatars/default.png';
  };

  // Divide os campos em três colunas
  const column1Fields = [
    "name",
    "age",
    "location",
    "description",
    "data_path"
  ];
  const column2Fields = [
    "education",
    "tech_skills",
    "soft_skills",
    "strenghts",
  ];
  const column3Fields = [
    "weaknesses",
    "goals",
    "hobbies",
    "personality",
  ];

  if (loadingAvatars) {
    return (
      <div className="persona-create-form" style={{ padding: "60px", textAlign: "center" }}>
        <h2 style={{ color: "var(--text-primary)", marginBottom: 16 }}>Loading avatars...</h2>
        <div style={{ color: "var(--text-secondary)" }}>Please wait</div>
      </div>
    );
  }

  return (
    <form
      className="persona-create-form"
      onSubmit={handleSubmit}
    >
      <h2 style={{ textAlign: "center", marginBottom: 16, color: "var(--text-primary)" }}>Nova Persona</h2>
      
      {/* Avatar Carousel */}
      <div className="avatar-carousel-container">
        <h3 style={{ textAlign: "center", marginBottom: 12, color: "var(--text-primary)", fontSize: "1.1rem" }}>
          Choose Avatar
        </h3>
        <div className="avatar-carousel">
          <button
            type="button"
            className="carousel-arrow carousel-arrow-left"
            onClick={handlePrevAvatar}
            disabled={loading}
          >
            ‹
          </button>
          <div className="avatar-display">
            <img
              src={`/avatars/${availableAvatars[selectedAvatarIndex]}.png`}
              alt={`Avatar ${selectedAvatarIndex + 1}`}
              className="carousel-avatar"
              onError={handleImageError}
            />
          </div>
          <button
            type="button"
            className="carousel-arrow carousel-arrow-right"
            onClick={handleNextAvatar}
            disabled={loading}
          >
            ›
          </button>
        </div>
        <div className="avatar-indicators">
          {availableAvatars.map((_, index) => (
            <span
              key={index}
              className={`avatar-indicator ${index === selectedAvatarIndex ? 'active' : ''}`}
              onClick={() => setSelectedAvatarIndex(index)}
            />
          ))}
        </div>
      </div>

      <div className="persona-create-form-fields" style={{ display: "flex", gap: "32px", width: "100%" }}>
        <div className="persona-create-form-col" style={{ flex: 1 }}>
          {column1Fields.map((key) => (
            <div key={key} style={{ marginBottom: 16 }}>
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
          {column2Fields.map((key) => (
            <div key={key} style={{ marginBottom: 16 }}>
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
        <div className="persona-create-form-col" style={{ flex: 1 }}>
          {column3Fields.map((key) => (
            <div key={key} style={{ marginBottom: 16 }}>
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
