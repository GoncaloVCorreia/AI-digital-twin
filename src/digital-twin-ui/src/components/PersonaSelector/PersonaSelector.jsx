import React, { useRef, useEffect, useState } from "react";
import "./PersonaSelector.css";

const personas = ["Rafael", "Maria", "Joao", "Ana"];

export default function PersonaSelector({ selected, setSelected }) {
  const containerRef = useRef();
  const [positions, setPositions] = useState({}); // posição original de cada círculo

  // Guardar posições originais quando o componente monta
  useEffect(() => {
    const newPositions = {};
    personas.forEach((p) => {
      const el = document.getElementById(`persona-${p}`);
      if (el && containerRef.current) {
        const circleRect = el.getBoundingClientRect();
        const containerRect = containerRef.current.getBoundingClientRect();
        newPositions[p] = {
          top: circleRect.top - containerRect.top,
          left: circleRect.left - containerRect.left,
          width: circleRect.width,
          height: circleRect.height,
        };
      }
    });
    setPositions(newPositions);
  }, []);

  return (
    <div className="persona-selector" ref={containerRef}>
      {personas.map((p) => {
        const isActive = selected === p;

        let style = {};
        if (positions[p] && containerRef.current) {
          const containerRect = containerRef.current.getBoundingClientRect();
          const circle = positions[p];
          if (isActive) {
            const centerX = containerRect.width / 2; // centro horizontal do container
            const targetY = -20; // altura abaixo do título
            const dx = centerX - (circle.left + circle.width / 2);
            const dy = targetY - circle.top;
            style = {
              position: "absolute",
              top: `${circle.top}px`,
              left: `${circle.left}px`,
              transform: `translate(${dx}px, ${dy}px) scale(1.5)`,
              zIndex: 10,
              transition: "transform 0.6s ease-in-out",
            };
          } else {
            style = {
              position: "absolute",
              top: `${circle.top}px`,
              left: `${circle.left}px`,
              zIndex: 1,
              transform: "translate(0,0) scale(1)",
              transition: "transform 0.6s ease-in-out",
            };
          }
        }

        return (
          <div
            key={p}
            id={`persona-${p}`}
            className={`persona-circle ${isActive ? "active" : ""}`}
            style={style}
            onClick={() => setSelected(p)}
          >
            <span className="persona-name">{p}</span>
          </div>
        );
      })}
    </div>
  );
}
