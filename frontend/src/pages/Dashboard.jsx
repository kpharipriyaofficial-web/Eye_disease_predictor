import { useState } from "react";
import ImageDropzone from "../components/upload/ImageDropzone";
import ResultCard from "../components/prediction/ResultCard";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import { predictImage } from "../api/predictions";
import { getErrorMessage } from "../api/client";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");

  function handleFileSelected(f) {
    setFile(f);
    setResult(null);
    setError("");
  }

  async function handleAnalyze() {
    if (!file) return;
    setScanning(true);
    setError("");
    setResult(null);
    try {
      const data = await predictImage(file);
      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err, "The prediction request failed. Please try again."));
    } finally {
      setScanning(false);
    }
  }

  function handleReset() {
    setFile(null);
    setResult(null);
    setError("");
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-hi">Analyze an eye image</h2>
        <p className="mt-1 text-sm text-text-mid">
          Upload a clear eye image and the model will return a prediction.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <ImageDropzone file={file} onFileSelected={handleFileSelected} scanning={scanning} />

          {error && (
            <p className="mt-4 rounded-lg border border-signal-red/30 bg-signal-red/5 px-3 py-2 text-xs text-signal-red">
              {error}
            </p>
          )}

          <div className="mt-5 flex gap-3">
            <Button
              variant="primary"
              onClick={handleAnalyze}
              disabled={!file}
              loading={scanning}
              className="flex-1"
            >
              {scanning ? "Analyzing…" : "Analyze image"}
            </Button>
            <Button variant="secondary" onClick={handleReset} disabled={scanning}>
              Reset
            </Button>
          </div>
        </Card>

        <div>
          {result ? (
            <ResultCard result={result} />
          ) : (
            <Card className="flex h-full min-h-[280px] items-center justify-center p-6 text-center">
              <p className="text-sm text-text-dim">
                Your prediction result will appear here after analysis.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
