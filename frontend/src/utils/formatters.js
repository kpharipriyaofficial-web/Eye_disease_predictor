/**
 * Normalizes a confidence value that could arrive as either a 0-1 fraction
 * or a 0-100 percentage (the API contract doesn't pin this down) and
 * returns a display string like "92.4%".
 */
export function formatConfidence(value) {
  const num = Number(value);
  if (Number.isNaN(num)) return "—";
  const percent = num <= 1 ? num * 100 : num;
  return `${percent.toFixed(1)}%`;
}

export function formatDate(isoString) {
  if (!isoString) return "—";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return isoString;
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
