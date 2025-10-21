import React, { useEffect } from "react";
import { getAvatarUrl } from "../../utils/avatarUtils";
import "./PersonaSelector.css";

export default function PersonaSelector({ selected, setSelected, horizontal, persona, showAddButton, onAddClick, personas = [], disabled = false, deleteMode = false, onDeleteClick, onPersonaDelete }) {
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

  // Handle image error by falling back to default
  const handleImageError = (e) => {
    e.target.src = '/avatars/default.png';
  };

  // Debug: show if no personas
  if (personasArray.length === 0) {
    console.log("No personas to display");
  }

  return (
    <>
      {horizontal && (
        <h2 style={{
          textAlign: 'center',
          fontSize: '1.8rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          marginBottom: '32px',
          marginTop: '0',
          letterSpacing: '0.5px'
        }}>
          Select the Persona
        </h2>
      )}
      <div className={`persona-selector${horizontal ? " horizontal" : ""}${disabled ? " disabled" : ""}${deleteMode ? " delete-mode" : ""}`}>
        {horizontal
          ? (
            <>
              {personasArray.map((p) => {
                const isActive = personaName?.toLowerCase() === p.name?.toLowerCase();
                return (
                  <div
                    key={p.id || p.name}
                    id={`persona-${p.name}`}
                    className={`persona-circle${isActive ? " active" : ""}${disabled ? " disabled" : ""}${deleteMode ? " deletable" : ""}`}
                    onClick={() => {
                      if (disabled) return;
                      if (deleteMode) {
                        onPersonaDelete && onPersonaDelete(p);
                      } else {
                        setSelected(p.name);
                      }
                    }}
                    style={{ cursor: disabled ? 'not-allowed' : (deleteMode ? 'pointer' : 'pointer'), opacity: disabled ? 0.6 : 1 }}
                  >
                    <img
                      src={getAvatarUrl(p)}
                      alt={p.name}
                      className="persona-avatar"
                      onError={handleImageError}
                    />
                    <span className="persona-name">{p.name}</span>
                    {deleteMode && <div className="delete-overlay">×</div>}
                  </div>
                );
              })}
              {showAddButton && (
                <div
                  className={`persona-circle persona-add-circle${disabled ? " disabled" : ""}`}
                  onClick={() => !disabled && onAddClick()}
                  title="Add Persona"
                  style={{ cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1 }}
                >
                  <img
                    src="/avatars/plus.png"
                    alt="add"
                    className="persona-avatar"
                    onError={handleImageError}
                  />
                  <span className="persona-name">Add</span>
                </div>
              )}
              {showAddButton && personasArray.length > 0 && (
                <div
                  className={`persona-circle persona-delete-circle${disabled ? " disabled" : ""}${deleteMode ? " active" : ""}`}
                  onClick={() => !disabled && onDeleteClick && onDeleteClick()}
                  title={deleteMode ? "Cancel deletion" : "Delete persona"}
                  style={{ cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1 }}
                >
                  <img
                    src="/avatars/delete.png"
                    alt="delete"
                    className="persona-avatar"
                    onError={handleImageError}
                  />
                  <span className="persona-name">{deleteMode ? "Cancel" : "Delete"}</span>
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
                  src={getAvatarUrl(personaToShow)}
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
    </>
  );
}