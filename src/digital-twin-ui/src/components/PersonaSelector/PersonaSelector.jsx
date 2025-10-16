import React, { useEffect } from "react";
import "./PersonaSelector.css";

export default function PersonaSelector({ selected, setSelected, horizontal, persona, showAddButton, onAddClick, personas = [] }) {
  // Debug: log personas to see what we're receiving
  useEffect(() => {
    console.log("PersonaSelector received personas:", personas);
    console.log("Is array?", Array.isArray(personas));
  }, [personas]);

  // Ensure personas is always an array
  const personasArray = Array.isArray(personas) ? personas : [];

  // Usa persona como fallback se selected estiver null/undefined
  const personaName = selected || persona;
  const personaToShow = personasArray.find((p) => p.name?.toLowerCase() === personaName?.toLowerCase());

  // Helper function to get avatar URL with fallback
  const getAvatarUrl = (personaName) => {
    const avatarPath = `/avatars/${personaName?.toLowerCase()}.png`;
    // Try to use persona-specific avatar, fallback to default.png
    return avatarPath;
  };

  // Handle image error by falling back to default
  const handleImageError = (e) => {
    e.target.src = '/avatars/default.png';
  };

  // Debug: show if no personas
  if (personasArray.length === 0) {
    console.log("No personas to display");
  }

  return (
    <div className={`persona-selector${horizontal ? " horizontal" : ""}`}>
      {horizontal
        ? (
          <>
            {personasArray.map((p) => {
              const isActive = personaName?.toLowerCase() === p.name?.toLowerCase();
              return (
                <div
                  key={p.id || p.name}
                  id={`persona-${p.name}`}
                  className={`persona-circle${isActive ? " active" : ""}`}
                  onClick={() => setSelected(p.name)}
                >
                  <img
                    src={getAvatarUrl(p.name)}
                    alt={p.name}
                    className="persona-avatar"
                    onError={handleImageError}
                  />
                  <span className="persona-name">{p.name}</span>
                </div>
              );
            })}
            {showAddButton && (
              <div
                className="persona-circle persona-add-circle"
                onClick={onAddClick}
                title="Adicionar nova persona"
              >
                <img
                  src="/avatars/plus.png"
                  alt="add"
                  className="persona-avatar"
                  onError={handleImageError}
                />
                <span className="persona-name">Adicionar</span>
              </div>
            )}
          </>
        )
        : personaToShow ? (
            <div
              key={personaToShow.id || personaToShow.name}
              id={`persona-${personaToShow.name}`}
              className="persona-circle active"
            >
              <img
                src={getAvatarUrl(personaToShow.name)}
                alt={personaToShow.name}
                className="persona-avatar"
                style={{
                  width: "100%",
                  height: "auto",
                  objectFit: "contain",
                }}
                onError={handleImageError}
              />
            </div>
          ) : null}
    </div>
  );
}