import Card from "../ui/Card";
import { formatConfidence } from "../../utils/formatters";

// /predict returns an open object (additionalProperties: string|number) —
// no field names are guaranteed by the API contract. We look for the
// conventional keys case-insensitively but never assume they exist.
function findKey(result, candidates) {
  const keys = Object.keys(result);
  for (const candidate of candidates) {
    const match = keys.find((k) => k.toLowerCase() === candidate);
    if (match) return match;
  }
  return null;
}

export default function ResultCard({ result }) {
  if (!result) return null;

  const predictionKey = findKey(result, ["prediction", "predicted_class", "class", "label"]);
  const confidenceKey = findKey(result, ["confidence", "score", "probability"]);
  const prediction = predictionKey ? result[predictionKey] : null;
  const confidence = confidenceKey ? result[confidenceKey] : null;

  const otherEntries = Object.entries(result).filter(
    ([key]) => key !== predictionKey && key !== confidenceKey
  );

  return (
    <Card className="animate-fade-up p-6">
      <div className="mb-5 flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-text-mid">AI prediction</span>
        <span className="rounded-full border border-line px-2.5 py-1 font-mono text-[11px] text-accent-cyan">
          model result
        </span>
      </div>

      {prediction !== null ? (
        <h2 className="mb-4 font-display text-2xl font-semibold text-text-hi">
          {String(prediction)}
        </h2>
      ) : (
        <p className="mb-4 text-sm text-text-mid">
          The model returned a result, but no recognizable prediction field. See details below.
        </p>
      )}

      {confidence !== null && !Number.isNaN(Number(confidence)) && (
        <div className="mb-5">
          <div className="mb-1.5 flex items-center justify-between text-xs">
            <span className="text-text-mid">Confidence</span>
            <span className="font-mono text-accent-cyan">{formatConfidence(confidence)}</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-raised">
            <div
              className="h-full rounded-full bg-gradient-to-r from-accent-cyan to-accent-blue"
              style={{ width: formatConfidence(confidence) }}
            />
          </div>
        </div>
      )}

      {otherEntries.length > 0 && (
        <div className="mt-4 grid grid-cols-2 gap-3 border-t border-line pt-4">
          {otherEntries.map(([key, value]) => (
            <div key={key}>
              <p className="text-[11px] uppercase tracking-wide text-text-dim">{key}</p>
              <p className="truncate font-mono text-sm text-text-hi">{String(value)}</p>
            </div>
          ))}
        </div>
      )}

      <p className="mt-6 border-t border-line pt-4 text-xs leading-relaxed text-text-dim">
        This tool provides an AI-generated prediction for informational and research purposes
        only. It is not a substitute for professional medical diagnosis — please consult an
        eye-care professional.
      </p>
    </Card>
  );
}
