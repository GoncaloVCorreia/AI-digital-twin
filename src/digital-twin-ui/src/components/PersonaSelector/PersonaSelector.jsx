import React from "react";
import "./PersonaSelector.css";

const personas = ["Rafael", "Maria", "Joao", "Ana"];

export default function PersonaSelector({ selected, setSelected }) {
  return (
    <div className="persona-selector">
      {personas.map((p) => {
        const isActive = selected === p;
        return (
          <div
            key={p}
            id={`persona-${p}`}
            className={`persona-circle ${isActive ? "active" : ""}`}
            onClick={() => setSelected(p)}
          >
            <span className="persona-name">{p}</span>
          </div>
        );
      })}
    </div>
  );
}