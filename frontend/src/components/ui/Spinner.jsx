const SIZES = { sm: "h-4 w-4 border-2", md: "h-6 w-6 border-2", lg: "h-10 w-10 border-[3px]" };

export default function Spinner({ size = "md", className = "" }) {
  return (
    <span
      className={`inline-block animate-spin rounded-full border-accent-cyan border-t-transparent ${SIZES[size]} ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
