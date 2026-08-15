import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import EmptyState from "../components/ui/EmptyState";
import Button from "../components/ui/Button";
import { getHistory } from "../api/predictions";
import { getErrorMessage } from "../api/client";
import { formatConfidence, formatDate } from "../utils/formatters";

const PAGE_SIZE = 10;

export default function History() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    getHistory({ page, pageSize: PAGE_SIZE })
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err, "Could not load your history."));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [page]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-hi">Prediction history</h2>
        <p className="mt-1 text-sm text-text-mid">
          Every analysis you've run, newest first.
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <Spinner size="lg" />
        </div>
      )}

      {!loading && error && (
        <p className="rounded-lg border border-signal-red/30 bg-signal-red/5 px-4 py-3 text-sm text-signal-red">
          {error}
        </p>
      )}

      {!loading && !error && data && data.items.length === 0 && (
        <EmptyState
          title="No predictions yet"
          description="Analyze an eye image from the dashboard and it will show up here."
        />
      )}

      {!loading && !error && data && data.items.length > 0 && (
        <>
          <Card className="overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-wide text-text-dim">
                  <th className="px-5 py-3 font-medium">Prediction</th>
                  <th className="px-5 py-3 font-medium">Confidence</th>
                  <th className="px-5 py-3 font-medium">Image</th>
                  <th className="px-5 py-3 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item) => (
                  <tr key={item.id} className="border-b border-line/60 last:border-0">
                    <td className="px-5 py-3.5 font-medium text-text-hi">{item.prediction}</td>
                    <td className="px-5 py-3.5 font-mono text-accent-cyan">
                      {formatConfidence(item.confidence)}
                    </td>
                    <td className="max-w-[180px] truncate px-5 py-3.5 font-mono text-text-mid">
                      {item.image_name}
                    </td>
                    <td className="px-5 py-3.5 text-text-mid">{formatDate(item.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <div className="flex items-center justify-between">
            <p className="text-xs text-text-dim">
              Page {data.page} of {totalPages} · {data.total} total
            </p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Previous
              </Button>
              <Button
                variant="secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
