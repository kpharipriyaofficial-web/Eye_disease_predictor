import { Link } from "react-router-dom";
import Button from "../components/ui/Button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-void px-6 text-center">
      <span className="font-mono text-sm text-accent-cyan">404</span>
      <h1 className="font-display text-2xl font-semibold text-text-hi">Page not found</h1>
      <p className="text-sm text-text-mid">The page you're looking for doesn't exist.</p>
      <Button as={Link} to="/" variant="primary" className="mt-2">
        Back to home
      </Button>
    </div>
  );
}
