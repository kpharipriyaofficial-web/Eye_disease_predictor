export default function Input({ label, id, error, className = "", ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-xs font-medium text-text-mid">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`rounded-lg border bg-surface px-3.5 py-2.5 text-sm text-text-hi placeholder:text-text-dim outline-none transition-colors focus:border-accent-cyan/60 ${
          error ? "border-signal-red/50" : "border-line"
        } ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-signal-red">{error}</span>}
    </div>
  );
}
