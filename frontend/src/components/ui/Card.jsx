export default function Card({ className = "", children, ...props }) {
  return (
    <div
      className={`rounded-2xl border border-line bg-surface/80 backdrop-blur-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
