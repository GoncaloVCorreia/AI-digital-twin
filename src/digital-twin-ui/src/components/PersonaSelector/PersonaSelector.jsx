import React from "react";

export default function PersonaSelector({ selected, setSelected }) {
  const personas = ["Rafael", "Maria", "Joao", "Ana"];

  return (
    <div className="persona-selector">
      {personas.map((p) => (
        <button
          key={p}
          className={selected === p ? "selected" : ""}
          onClick={() => setSelected(p)}
        >
          {p}
        </button>
      ))}
    </div>
  );
}
