import { useCallback, useRef, useState } from "react";

export default function ImageDropzone({ file, onFileSelected, scanning = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const previewUrl = file ? URL.createObjectURL(file) : null;

  const acceptFile = useCallback(
    (candidate) => {
      if (!candidate) return;
      if (!candidate.type.startsWith("image/")) {
        setError("Please select an image file.");
        return;
      }
      setError("");
      onFileSelected(candidate);
    },
    [onFileSelected]
  );

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    acceptFile(e.dataTransfer.files?.[0]);
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative flex aspect-[16/9] w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-2xl border transition-colors ${
          isDragging
            ? "border-accent-cyan bg-accent-cyan/5"
            : "border-line bg-surface hover:border-accent-cyan/40"
        }`}
      >
        {/* ambient / active scan sweep — the signature motif */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div
            className={`absolute inset-x-0 h-24 bg-gradient-to-b from-transparent via-accent-cyan/20 to-transparent ${
              scanning ? "animate-scan" : "animate-scan opacity-30"
            }`}
          />
        </div>

        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Selected eye scan preview"
            className="absolute inset-0 h-full w-full object-contain bg-void/40 p-3"
          />
        ) : (
          <div className="relative z-10 flex flex-col items-center gap-3 px-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border border-accent-cyan/30 text-accent-cyan">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
                <path d="M12 3v12" strokeLinecap="round" />
                <path d="m7 8 5-5 5 5" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
              </svg>
            </div>
            <p className="text-sm text-text-hi">
              <span className="text-accent-cyan">Click to upload</span> or drag an eye image here
            </p>
            <p className="text-xs text-text-dim">JPG or PNG</p>
          </div>
        )}

        {scanning && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-void/50 backdrop-blur-[2px]">
            <div className="relative flex h-16 w-16 items-center justify-center">
              <span className="absolute inline-flex h-full w-full animate-pulse-ring rounded-full border border-accent-cyan" />
              <span className="h-3 w-3 rounded-full bg-accent-cyan" />
            </div>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => acceptFile(e.target.files?.[0])}
        />
      </div>
      {error && <p className="mt-2 text-xs text-signal-red">{error}</p>}
      {file && !scanning && (
        <p className="mt-2 truncate font-mono text-xs text-text-mid">{file.name}</p>
      )}
    </div>
  );
}
