export default function MessageBubble({ role, text }) {
  return (
    <div className={`message ${role}`}>
      <div className="bubble">{text}</div>
    </div>
  );
}
