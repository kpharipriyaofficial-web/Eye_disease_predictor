const VARIANTS = {
  primary:
    "bg-gradient-to-r from-accent-cyan to-accent-blue text-void font-semibold hover:shadow-glow-sm hover:brightness-110",
  secondary:
    "bg-surface-raised text-text-hi border border-line hover:bg-surface-hover",
  ghost: "bg-transparent text-text-mid hover:text-text-hi hover:bg-surface-raised",
  danger: "bg-transparent text-signal-red border border-signal-red/30 hover:bg-signal-red/10",
};

export default function Button({
  as: Component = "button",
  variant = "primary",
  className = "",
  disabled = false,
  loading = false,
  children,
  ...props
}) {
  return (
    <Component
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </Component>
  );
}
