import React from "react";
import "./PersonaSelector.css";

// Add avatar URLs for each persona
const personas = [
  { name: "rafael", avatar: "/avatars/rafael2.png" },
  { name: "garcia", avatar: "/avatars/garcia.png" },
  { name: "correia", avatar: "/avatars/correia.png" },
  { name: "francisco", avatar: "/avatars/francisco.png" },
];

export default function PersonaSelector({ selected, setSelected, horizontal, persona }) {
  // Usa persona como fallback se selected estiver null/undefined
  const personaName = selected || persona;
  const personaToShow = personas.find((p) => p.name === personaName);

  return (
    <div className={`persona-selector${horizontal ? " horizontal" : ""}`}>
      {horizontal
        ? personas.map((p) => {
            const isActive = personaName === p.name;
            return (
              <div
                key={p.name}
                id={`persona-${p.name}`}
                className={`persona-circle${isActive ? " active" : ""}`}
                onClick={() => setSelected(p.name)}
              >
                <img
                  src={p.avatar}
                  alt={p.name}
                  className="persona-avatar"
                  style={{
                    width: "100%",
                    height: "auto",
                    objectFit: "contain",
                  }}
                />
              </div>
            );
          })
        : personaToShow ? (
            <div
              key={personaToShow.name}
              id={`persona-${personaToShow.name}`}
              className="persona-circle active"
            >
              <img
                src={personaToShow.avatar}
                alt={personaToShow.name}
                className="persona-avatar"
                style={{
                  width: "100%",
                  height: "auto",
                  objectFit: "contain",
                }}
              />
            </div>
          ) : null}
    </div>
  );
}