export default function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-line px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full border border-line text-accent-cyan">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v5" strokeLinecap="round" />
          <circle cx="12" cy="16" r="0.6" fill="currentColor" />
        </svg>
      </div>
      <h3 className="font-display text-base text-text-hi">{title}</h3>
      {description && <p className="max-w-sm text-sm text-text-mid">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
