import { Link } from "react-router-dom";
import PublicNav from "../components/layout/PublicNav";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

const STEPS = [
  {
    n: "01",
    title: "Upload an eye image",
    desc: "Drag in a photo, or select one from your device. JPG and PNG are supported.",
  },
  {
    n: "02",
    title: "The model analyzes it",
    desc: "Your image is sent securely to the prediction API and processed by the trained model.",
  },
  {
    n: "03",
    title: "Review your result",
    desc: "See the predicted condition and confidence, saved automatically to your history.",
  },
];

const FEATURES = [
  {
    title: "Model-backed predictions",
    desc: "Every result comes directly from your FastAPI backend's trained model — nothing simulated.",
  },
  {
    title: "Full prediction history",
    desc: "Every analysis is recorded to your account so you can track results over time.",
  },
  {
    title: "Secure by design",
    desc: "Authenticated with a bearer token on every request; your data stays tied to your account.",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      <PublicNav />

      <section className="relative overflow-hidden px-6 pb-24 pt-20">
        <div className="grid-fade pointer-events-none absolute inset-0 opacity-60" />
        <div className="pointer-events-none absolute left-1/2 top-0 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-accent-cyan/10 blur-[120px]" />

        <div className="relative mx-auto max-w-3xl text-center">
          <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-line px-3 py-1 font-mono text-[11px] text-accent-cyan">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-cyan" />
            AI-assisted eye analysis
          </span>
          <h1 className="font-display text-4xl font-semibold leading-tight text-text-hi sm:text-5xl">
            Upload an eye image.
            <br />
            <span className="bg-gradient-to-r from-accent-cyan to-accent-blue bg-clip-text text-transparent">
              Get an AI prediction in seconds.
            </span>
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-text-mid">
            Eye_ML runs your images through a trained detection model and keeps a running history
            of every result, tied securely to your account.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Button as={Link} to="/register" variant="primary" className="px-6 py-3 text-base">
              Get started
            </Button>
            <Button as={Link} to="/login" variant="secondary" className="px-6 py-3 text-base">
              Log in
            </Button>
          </div>
        </div>

        {/* signature scan visual */}
        <div className="relative mx-auto mt-16 max-w-md">
          <Card className="relative aspect-square overflow-hidden p-0">
            <div className="pointer-events-none absolute inset-0 overflow-hidden">
              <div className="absolute inset-x-0 h-20 animate-scan bg-gradient-to-b from-transparent via-accent-cyan/25 to-transparent" />
            </div>
            <div className="flex h-full w-full items-center justify-center">
              <svg width="140" height="140" viewBox="0 0 24 24" fill="none" stroke="#4FD8F0" strokeWidth="1.2">
                <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z" opacity="0.8" />
                <circle cx="12" cy="12" r="3.4" />
                <circle cx="12" cy="12" r="6" opacity="0.35" />
                <circle cx="12" cy="12" r="8.5" opacity="0.15" />
              </svg>
            </div>
          </Card>
        </div>
      </section>

      <section className="border-t border-line px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-10 text-center font-display text-2xl font-semibold">How it works</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {STEPS.map((step) => (
              <Card key={step.n} className="p-6">
                <span className="font-mono text-xs text-accent-cyan">{step.n}</span>
                <h3 className="mt-3 font-display text-lg font-semibold text-text-hi">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm text-text-mid">{step.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-line px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-10 text-center font-display text-2xl font-semibold">
            Built for real use
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title}>
                <h3 className="font-display text-base font-semibold text-text-hi">{f.title}</h3>
                <p className="mt-2 text-sm text-text-mid">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-line px-6 py-10">
        <div className="mx-auto max-w-5xl text-center text-xs text-text-dim">
          Eye_ML is an AI-assisted research and educational tool. Predictions are not a medical
          diagnosis — always consult a qualified professional.
        </div>
      </footer>
    </div>
  );
}
